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

import sys
# setting path
sys.path.append('/usr/src/app')

from celery.result import AsyncResult
from worker import create_task, process_data, create_processing_task
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from fastapi import Body, FastAPI, Form, Request
from models.datamodel import DatasetConfig
import redis
import json
from itsdangerous import TimestampSigner
import re
import uuid
import base64


router = APIRouter()
templates = Jinja2Templates(directory="/usr/src/app/templates")

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)  # Create a Redis client


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@router.post("/tasks", status_code=201)
def run_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


# @router.post("/tasks_model", status_code=201)
# def run_task(payload : DatasetConfig):
#     payload_dict = payload.dict()
#     # task_duration = payload_dict["duration"]
#     task = create_processing_task.delay(payload_dict)
#     return JSONResponse({"task_id": task.id})


@router.get("/celery_tasks/{task_id}")
def get_celery_task_status(task_id):
    task_result = AsyncResult(task_id)
    value = redis_client.get(task_id)
    if value is not None:
        print("Value retrieved from Redis:", value.decode('utf-8'))  # Decode bytes to string if needed
        try:
            task_data = json.loads(value)
        except Exception as e:
            print('json.loads(value) failed with: ', e)
            task_data = value.decode('utf-8')
    else:
        print("Key not found in Redis.")
        task_data = value
    result = {
        "task_id": str(task_id),
        "task_status": str(task_result.status),
        "task_result": str(task_result.result),
        "task_data": task_data,
    }
    return JSONResponse(result)


@router.get("/tasks/{task_id}")
def get_status(task_id):
    value = redis_client.get(task_id)
    if value is not None:
        print("Value retrieved from Redis:", value.decode('utf-8'))  # Decode bytes to string if needed
        try:
            task_data = json.loads(value)
        except Exception as e:
            print('json.loads(value) failed with: ', e)
            task_data = value.decode('utf-8')
    else:
        print("Key not found in Redis.")
        task_data = value
    task_result = AsyncResult(str(task_id))
    result = {
        "task_id": str(task_id),
        "task_status": str(task_result.status),
        "task_result": str(task_result.result),
        "task_data": task_data,
    }
    return JSONResponse(result)

@router.get("/kill_tasks/{task_id}")
def kill_task(task_id):
    print(AsyncResult(str(task_id)))
    print(AsyncResult(str(task_id)).status)
    print(AsyncResult(str(task_id)).result)
    AsyncResult(str(task_id)).revoke(terminate=True)
    print(AsyncResult(str(task_id)))
    print(AsyncResult(str(task_id)).status)
    print(AsyncResult(str(task_id)).result)
    # AsyncResult(task_id).revoke(terminate=True)
    return JSONResponse({f'{task_id}': 'killed'})
    


# @router.post("/process", status_code=201)
# def run_task(payload = Body(...)):
#     task = process_data.delay(payload)
#     return JSONResponse({"task_id": task.id})



@router.post("/process_data", status_code=201)
def run_task(payload : DatasetConfig):
    payload_dict = payload.dict()
    # task_duration = payload_dict["duration"]
    
    # TODO: add to pyload_dict the download_token and filename
    
    
    rv = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")
    unique = re.sub(
        r"[\=\+\/]", lambda m: {"+": "-", "/": "_", "=": ""}[m.group(0)], rv
    )
    filename = str(unique) + f".{payload_dict['output_format']}"
    s = TimestampSigner("secret-key")
    download_token = s.sign(filename).decode()
    json_string = json.dumps({"download_token": download_token, "filename": filename})
    payload_dict['download_token'] = download_token
    payload_dict['filename'] = filename
    task = process_data.delay(payload_dict)
    redis_client.set(task.id, json_string)
    return JSONResponse({"task_id": task.id, "download_token": download_token, "filename": filename, "task_status": task.status})


