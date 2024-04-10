import base64
import uuid
from models.datamodel import BasketDatasource
import redis
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
import re
from worker import compress, compress2, generate_spec

router = APIRouter()
templates = Jinja2Templates(directory="/usr/src/app/templates")

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)  # Create a Redis client


@router.post("/api/compress")
async def enqueue_compress(dl: BasketDatasource):
    # We use celery delay method in order to enqueue the task with the given parameters
    rv = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")
    transaction_id = re.sub(
        r"[\=\+\/]", lambda m: {"+": "-", "/": "_", "=": ""}[m.group(0)], rv
    )
    print("#################################   ", transaction_id, dl.data)
    # TODO: set NOW the status of the transaction to 'in-progress' by adding a new data key 'status'
    status = {"status": False}
    redis_client.set(transaction_id, status)
    compress.delay(dl.data, transaction_id)
    return {"transaction_id": transaction_id}


@router.post("/api/compress_spec")
async def enqueue_compress2(dl: BasketDatasource):
    # We use celery delay method in order to enqueue the task with the given parameters
    rv = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")
    transaction_id = re.sub(
        r"[\=\+\/]", lambda m: {"+": "-", "/": "_", "=": ""}[m.group(0)], rv
    )
    print("#################################   ", transaction_id, dl.data)
    # TODO: set NOW the status of the transaction to 'in-progress' by adding a new data key 'status'
    status = {"status": False}
    redis_client.set(transaction_id, status)
    compress2.delay(dl.data, dl.notebooks, transaction_id)
    return {"transaction_id": transaction_id}


@router.post("/api/getspec")
async def enqueue_getspec(dl: BasketDatasource):
    # We use celery delay method in order to enqueue the task with the given parameters
    rv = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")
    transaction_id = re.sub(
        r"[\=\+\/]", lambda m: {"+": "-", "/": "_", "=": ""}[m.group(0)], rv
    )
    print("#################################   ", transaction_id, dl.data)
    # TODO: set NOW the status of the transaction to 'in-progress' by adding a new data key 'status'
    status = {"status": False}
    redis_client.set(transaction_id, status)
    print("this is what we get", dl)
    generate_spec.delay(dl.data, dl.notebooks, transaction_id)
    return {"transaction_id": transaction_id}

