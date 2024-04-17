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
