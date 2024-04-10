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

# import sys
# # setting path
# sys.path.append('/usr/src/app')

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="/usr/src/app/templates")

router = APIRouter()

@router.get("/task/status/render/{task_id}", response_class=HTMLResponse)
async def render_task_status(request: Request, task_id: str):
    # task_status = get_task_status(task_id)
    # , "task_status": 'task_status'
    return templates.TemplateResponse("stream.html", {"request": request, "task_id": task_id, "task_status": 'task_status'})
