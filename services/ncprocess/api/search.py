from fastapi import APIRouter
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
from models.datamodel import SearchObject
from models.datamodel import SearchObject 
from worker import csw_search
import json
import redis


router = APIRouter()
templates = Jinja2Templates(directory="/usr/src/app/templates")

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)  # Create a Redis client



@router.post("/csw_search", status_code=201)
def run_task(payload : SearchObject):
    payload_dict = payload.dict()
    task = csw_search.delay(payload_dict)
    json_string = json.dumps(payload_dict)
    redis_client.set(task.id, json_string)
    return JSONResponse({"task_id": task.id, "payload": payload_dict})
    

@router.get("/search", response_class=HTMLResponse)
async def read_root(request: Request, response: Response):
    client_choice = request.cookies.get("location_permission")
    if client_choice is None:
        # Default to asking for permission
        response.set_cookie(key="location_permission", value="ask")
    # context = {"key": "value"}
    # return templates.TemplateResponse("search.html", {"request": request, **context})
    context = {"request": request}
    return templates.TemplateResponse("search.html", context)


@router.post("/submit-form")
def submit_form(data: SearchObject):
    # Here you can access the submitted form data as attributes of the data object
    # For example: data.text_entry, data.start_time, etc.
    # You can perform any necessary processing or validation here
    # For demonstration purposes, let's just print the received data
    print("Received form data:")
    print("Text Entry:", data.text_entry)
    print("Start Time:", data.start_time)
    print("End Time:", data.end_time)
    print("Keywords List:", data.keywords_list)
    print("Bounding Box:", data.bbox)
    # Optionally, you can return a response
    return {"message": "Form data received successfully", "data": data}