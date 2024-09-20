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

import fastapi
from typing import List
from models.datamodel import BasketDatasource
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from fastapi import Query
from services import bokeh_service

templates = Jinja2Templates(directory="/app/templates")
router = fastapi.APIRouter()


@router.get("/dashboard", name="dashboard", response_model=BasketDatasource)
async def get_dashboard(
    request: Request,
    data: str = Query(
        None, title="dict of data", description="dict of data and meta informations"
    ),
):
    dashboard = bokeh_service.get_dashboard_script(data)
    return templates.TemplateResponse(
        "dashboard/embed.html", {"request": request, "app1": dashboard}
    )
