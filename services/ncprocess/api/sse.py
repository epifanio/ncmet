# This file is part of ncmet.
#
# https://github.com/metno/ncmet
#
# ncmet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ncmet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ncmet.  If not, see <http://www.gnu.org/licenses/>.

# import sys
# # setting path
# sys.path.append('/usr/src/app')

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="/app/templates")

router = APIRouter()

@router.get("/task/status/render/{task_id}", response_class=HTMLResponse)
async def render_task_status(request: Request, task_id: str):
    # task_status = get_task_status(task_id)
    # , "task_status": 'task_status'
    return templates.TemplateResponse("stream.html", {"request": request, "task_id": task_id, "task_status": 'task_status'})
