"""
====================

Copyright 2022 MET Norway

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import time
import sys
# setting path
sys.path.append('/app')


import redis
import json
from celery import Celery
from models.datamodel import DatasetConfig, SearchObject
# from redis_utility.redis_data import get_data, set_data 
import xarray as xr
import numpy as np
from pathlib import Path
# nc_aPi
import uuid
import base64
import re
from itsdangerous import TimestampSigner
import zipfile
import yaml
from celery.utils.log import get_task_logger
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates
from jsonschema import ValidationError, validate

#

download_dir = os.environ["DOWNLOAD_DIR"]
api_host = os.environ["API_HOST"]


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)  # Create a Redis client

logger = get_task_logger(__name__)


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    # Store data
    task_id = create_task.request.id
    data = {"status": False, 'download_token': 'download_token', 'filename': 'filename'}
    json_string = json.dumps(data)
    redis_client.set(task_id, json_string)
    return True

@celery.task(name="create_processing_task")
def create_processing_task(processing_task):
    time.sleep(int(10))
    # Store data
    task_id = create_processing_task.request.id
    # data = {"status": False, 'download_token': 'download_token', 'filename': 'filename'}
    json_string = json.dumps(processing_task)
    redis_client.set(task_id, json_string)
    return True

@celery.task(name="process_data")
def process_data(DatasetConfig_dict):
    
    print(DatasetConfig_dict)
    
    # Get the value of the environment variable DOWNLOAD_DIR
    download_dir = os.environ.get('DOWNLOAD_DIR')

    # If the environment variable is not set, you might want to handle it
    if download_dir is None:
        raise ValueError("DOWNLOAD_DIR environment variable is not set")
    
    task_id = process_data.request.id
    dcf = DatasetConfig()
    dcf.url = DatasetConfig_dict['url']
    dcf.variables = DatasetConfig_dict['variables']
    dcf.output_format = DatasetConfig_dict['output_format']
    
    print(str('start processing'))
    ds = xr.open_dataset(dcf.url, decode_times=dcf.decoded_time)
    time_coord = [i for i in ds.coords if ds.coords.dtypes[i] == np.dtype('<M8[ns]')]
    time_dim = time_coord[0]

    if len(time_coord) != 0:
        dcf.decoded_time = True
    else:
        dcf.decoded_time = False
    try:
        dcf.time_range = [DatasetConfig_dict['time_range'][0], DatasetConfig_dict['time_range'][1]]
    except IndexError:
        dcf.time_range = [ds.indexes[time_coord[0]].min(), ds.indexes[time_coord[0]].max()]
    dcf.is_resampled = False

    data_selected = {}
        
    if dcf.decoded_time:
        for time_dim in time_coord:
            data_selected[time_dim] = ds[dcf.variables].sel({time_dim: slice(dcf.time_range[0], 
                                                                                       dcf.time_range[1])})
        merged_dataset = xr.merge(data_selected.values())
    else:
        merged_dataset = ds[dcf.variables]
        
    filename = DatasetConfig_dict['filename']
    # Construct the path using pathlib
    file_path = Path(download_dir) / filename
    print("filename : ", filename)
    
    print("output_format : ", dcf.output_format)    
    if dcf.is_resampled:
        pass
    
    if dcf.output_format in ['csv', 'CSV']:
        try:
            # merged_dataset.to_netcdf(f"{os.getenv('DOWNLOAD_DIR')}/{time_dim}_selected_data.nc")
            print(f"attempting to save the dataset as CSV file... in {file_path}")
            df = merged_dataset.to_dataframe()
            df.to_csv(file_path)
        except ValueError:
            print(f"attempting to save the dataset as CSV file... as {file_path} failed")
            # encoding = {i:{'_FillValue': np.nan} for i in ds[dcf.variables]}
            # merged_dataset.to_netcdf(f"{os.getenv('DOWNLOAD_DIR')}/{time_dim}_selected_datca.nc", encoding=encoding)
            # df = merged_dataset.to_dataframe()
            # df.to_csv(file_path)
            # merged_dataset.to_csv(file_path, encoding=encoding)
            filename = filename.replace(dcf.output_format, 'nc')
            print(f"will try to download as netcdf {file_path} ")
            pass
    else:
        # filename = f"{os.getenv('DOWNLOAD_DIR')}/{time_dim}_selected_data.nc"
        # File name string
        # filename = f"{time_dim}_selected_data.nc"
        
        print(f"attempting to save the dataset as netcdf file... in {file_path}")
        try:
            # merged_dataset.to_netcdf(f"{os.getenv('DOWNLOAD_DIR')}/{time_dim}_selected_data.nc")
            merged_dataset.to_netcdf(file_path)
        except ValueError:
            print(f"attempting to save the dataset as netcdf file... with encoding...in {file_path}")
            encoding = {i:{'_FillValue': np.nan} for i in ds[dcf.variables]}
            # merged_dataset.to_netcdf(f"{os.getenv('DOWNLOAD_DIR')}/{time_dim}_selected_datca.nc", encoding=encoding)
            merged_dataset.to_netcdf(file_path, encoding=encoding)
    # redis_client.set(task_id, json_string)
    # # set the dataset status to processing itno redis
    # data = {"status": False, 'download_token': 'download_token', 'filename': 'filename'}
    # set_data(
    #     transaction_id='download_token',
    #     data=data,
    #     redishost=os.environ["REDIS_HOST"],
    #     password=os.environ["REDIS_PASSWORD"],
    # )
    # # and start processing the dataset
    # time.sleep(100)
    print(str("completed processing"))
    # store the process resutls into redis and change the status of the task
    print(str(dcf))
    return True

@celery.task(name="csw_search")
def csw_search(SearchObject_dict):
    print(SearchObject_dict)
    return True

@celery.task
def compress(data, transaction_id):
    rv = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")
    unique = re.sub(
        r"[\=\+\/]", lambda m: {"+": "-", "/": "_", "=": ""}[m.group(0)], rv
    )
    filename = str(unique) + ".zip"
    outfile = Path(download_dir, str(filename))
    s = TimestampSigner("secret-key")
    download_token = s.sign(filename).decode()
    zip_file = zipfile.ZipFile(outfile, "a")

    yaml_filename = str(unique) + ".yaml"
    yaml_outfile = Path(download_dir, str(yaml_filename))
    with open(yaml_outfile, "w+") as yaml_file:
        yaml.dump(data, yaml_file, allow_unicode=True)
    zip_file.write(yaml_outfile, os.path.basename(yaml_outfile))

    for i in data:
        if "opendap" in data[i]["resources"]:
            nc_url = data[i]["resources"]["opendap"][0]
            logger.info(f"processing {i} in {filename}")
            try:
                with xr.open_dataset(nc_url, decode_cf=False) as ds:
                    try:
                        nc_name = nc_url.split("/")[-1]
                        ds.to_netcdf(nc_name)
                    except:
                        logger.debug(f"failed processing {i}")
                    try:
                        zip_file.write(nc_name, os.path.basename(nc_name))
                    except:
                        logger.debug(f"failed processing {i}")
                logger.info(f"Compressing {i} in {filename}")
            except FileNotFoundError:
                print(f"resource {nc_url} is not a valid opendap resource")
    zip_file.close()
    env = Environment(loader=FileSystemLoader("""/app/templates"""))
    template = env.get_template("download/mail_download.html")
    url = f"https://{api_host}/api/download/{download_token}"
    output = template.render(data=data, date=dt.datetime.now().isoformat(), url=url)
    data["download_url"] = url
    transaction_id_data = transaction_id + "_data"
    redis_client.set(transaction_id_data, data)
    time.sleep(1)
    status = {"status": True}
    redis_client.set(transaction_id, status)
    print(url, transaction_id, data)
    
@celery.task
def compress2(data, notebooks, transaction_id):
    rv = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")
    unique = re.sub(
        r"[\=\+\/]", lambda m: {"+": "-", "/": "_", "=": ""}[m.group(0)], rv
    )
    filename = str(unique) + ".zip"
    outfile = Path(download_dir, str(filename))
    s = TimestampSigner("secret-key")
    download_token = s.sign(filename).decode()
    zip_file = zipfile.ZipFile(outfile, "a")

    data = {"data": data, "notebooks": notebooks}
    datasets = [
        {
            "id": i,
            "title": data["data"][i]["title"],
            "resource": data["data"][i]["resources"][
                list(data["data"][i]["resources"].keys())[0]
            ][0],
            "type": list(data["data"][i]["resources"].keys())[0],
        }
        for i in data["data"]
    ]
    notebooks = [
        {
            "resource": data["notebooks"][i]["resource"],
            "type": "jupyter",
            "dependencies": [],
        }
        for i in data["notebooks"]
    ]
    print(data["notebooks"])
    notebooks = [
        {
            "name": i,
            "resource": data["notebooks"][i]["resource"],
            "dependencies": [
                {
                    "name": j["name"],
                    # library dependencies are hardcoded to an emty array
                    # can be extended if really needed
                    "dependencies": [],
                    "resource": j["resource"],
                    "version": j["version"],
                }
                for j in data["notebooks"][i]["dependencies"]
            ],
        }
        for i in data["notebooks"]
    ]

    # context is hardocoded here
    # need to generate a uuid
    # dependencies for the dependencies are set to be empty
    context = {"type": "VRE config", "id": str(uuid.uuid4())}
    environment = {"provider": "PTEP", "processor": "JupyterHub"}
    templates = Jinja2Templates(directory="/app/templates")
    # ff = templates.get_template("config/obj_tmpl.yaml").render(
    #    {"request": "request", "datasets": datasets, "notebooks": notebooks}
    # )

    ff = templates.get_template("config/ptep_obj_tmpl.yaml").render(
        {
            "request": "request",
            "datasets": datasets,
            "notebooks": notebooks,
            "context": context,
            "environment": environment,
        }
    )

    print(ff)
    try:
        with open("/app/config/info_object_schema.json") as f:
            information_object_schema = json.loads(f.read())
            validate(instance=ff, schema=information_object_schema)
    except ValidationError:
        print("generated yaml not valid")

    yaml_filename = str(unique) + ".yaml"
    yaml_outfile = Path(download_dir, str(yaml_filename))
    with open(yaml_outfile, "w+") as yaml_file:
        ##yaml.dump(data, yaml_file, allow_unicode=True)
        yaml_file.write(ff)
    zip_file.write(yaml_outfile, os.path.basename(yaml_outfile))
    datasets = data["data"]
    for i in datasets:
        # print("################## DATA  ############################## \n")
        # print("data: ", data)
        # print("#################  DATA[i] ############################### \n")
        # print("data[i]: ", data[i])
        # print("######################## i ######################## \n  i: ", i)
        if "opendap" in datasets[i]["resources"]:
            nc_url = datasets[i]["resources"]["opendap"][0]
            logger.info(f"processing {i} in {filename}")
            try:
                with xr.open_dataset(nc_url, decode_cf=False) as ds:
                    try:
                        nc_name = nc_url.split("/")[-1]
                        ds.to_netcdf(nc_name)
                    except:
                        logger.debug(f"failed processing {i}")
                    try:
                        zip_file.write(nc_name, os.path.basename(nc_name))
                    except:
                        logger.debug(f"failed processing {i}")
                logger.info(f"Compressing {i} in {filename}")
            except FileNotFoundError:
                print(f"resource {nc_url} is not a valid opendap resource")
    zip_file.close()
    env = Environment(loader=FileSystemLoader("""/app/templates"""))
    template = env.get_template("download/mail_download.html")
    url = f"https://{api_host}/api/download/{download_token}"
    output = template.render(data=data, date=dt.datetime.now().isoformat(), url=url)
    data["download_url"] = url
    transaction_id_data = transaction_id + "_data"
    redis_client.set(transaction_id_data, data)
    time.sleep(1)
    status = {"status": True}
    redis_client.set(transaction_id, status)
    print(url, transaction_id, data)
    
@celery.task
def generate_spec(data, notebooks, transaction_id):
    print(data)
    data = {"data": data, "notebooks": notebooks}
    rv = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")
    unique = re.sub(
        r"[\=\+\/]", lambda m: {"+": "-", "/": "_", "=": ""}[m.group(0)], rv
    )
    filename = str(unique) + ".yaml"
    outfile = Path(download_dir, str(filename))
    s = TimestampSigner("secret-key")
    download_token = s.sign(filename).decode()
    datasets = [
        {
            "id": i,
            "title": data["data"][i]["title"],
            "resource": data["data"][i]["resources"][
                list(data["data"][i]["resources"].keys())[0]
            ][0],
            "type": list(data["data"][i]["resources"].keys())[0],
        }
        for i in data["data"]
    ]
    notebooks = [
        {
            "resource": data["notebooks"][i]["resource"],
            "type": "jupyter",
            "dependencies": [],
        }
        for i in data["notebooks"]
    ]
    print(data["notebooks"])
    notebooks = [
        {
            "name": i,
            "resource": data["notebooks"][i]["resource"],
            "virtual_environment_type": data["notebooks"][i][
                "virtual_environment_type"
            ],
            "dependencies": [
                {
                    "name": j["name"],
                    # library dependencies are hardcoded to an emty array
                    # can be extended if really needed
                    "dependencies": [],
                    "resource": j["resource"],
                    "version": j["version"],
                }
                for j in data["notebooks"][i]["dependencies"]
            ],
        }
        for i in data["notebooks"]
    ]

    # context is hardocoded here
    # need to generate a uuid
    # dependencies for the dependencies are set to be empty
    context = {"type": "VRE config", "id": str(uuid.uuid4())}
    environment = {"provider": "PTEP", "processor": "JupyterHub"}
    templates = Jinja2Templates(directory="/app/templates")
    # ff = templates.get_template("config/obj_tmpl.yaml").render(
    #    {"request": "request", "datasets": datasets, "notebooks": notebooks}
    # )

    ff = templates.get_template("config/ptep_obj_tmpl.yaml").render(
        {
            "request": "request",
            "datasets": datasets,
            "notebooks": notebooks,
            "context": context,
            "environment": environment,
        }
    )

    print(ff)
    try:
        with open("/app/config/info_object_schema.json") as f:
            information_object_schema = json.loads(f.read())
            validate(instance=ff, schema=information_object_schema)
    except ValidationError as e:
        print("generated yaml not valid: ", e)

    with open(outfile, "w+") as yaml_file:
        ##yaml.dump(data, yaml_file, allow_unicode=True)
        yaml_file.write(ff)

    env = Environment(loader=FileSystemLoader("""/app/templates"""))
    template = env.get_template("download/mail_download.html")
    url = f"https://{api_host}/api/download/{download_token}"
    output = template.render(data=data, date=dt.datetime.now().isoformat(), url=url)
    data["download_url"] = url
    transaction_id_data = transaction_id + "_data"
    redis_client.set(transaction_id_data, data)
    time.sleep(1)
    status = {"status": True}
    redis_client.set(transaction_id, status)
    print(url, transaction_id, data)


