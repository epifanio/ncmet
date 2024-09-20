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

import logging
import sys
sys.path.append('/app')
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from api import celery_task
from api import auth
from api import sse
from api import download
from api import search
from api import nc_api


import os

download_dir = os.getenv("DOWNLOAD_DIR")

if download_dir:
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"Created directory: {download_dir}")
    else:
        print(f"Directory already exists: {download_dir}")
else:
    print("DOWNLOAD_DIR environment variable not set.")


logging.getLogger('passlib').setLevel(logging.ERROR)

app = FastAPI(
    title="ncapi",
    description="Prototype API to process NetCDF Data",
    version="0.0.1",
)




favicon_path = 'favicon.ico'

@app.get('/app/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_PROCESSING_SECOND = 600

def configure():
    """ run the routing configuration for the mail fastapi App"""
    configure_routing()
    
def configure_routing():    
    app.mount("/static", StaticFiles(directory="/app/static"), name="static")
    app.mount("/download", StaticFiles(directory=download_dir), name="download")
    app.include_router(celery_task.router)
    app.include_router(sse.router)
    app.include_router(download.router)
    app.include_router(search.router)
    # app.include_router(nc_api.router)
    app.include_router(auth.router)
    

if __name__ == "__main__":
    configure()
    uvicorn.run(app, port=8000, host="0.0.0.0", reload=True, debug=True)
else:
    configure()
