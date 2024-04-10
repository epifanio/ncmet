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
