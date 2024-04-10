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

from pydantic import BaseModel, Field, AnyUrl
from typing import List, Optional
from datetime import date, datetime, time, timedelta


class DatasetConfig(BaseModel):
    url: str = Field('', description="The URL for the dataset")
    variables: List[str] = Field([], description="List of variables in the dataset")
    decoded_time: bool = Field(True, description="Flag indicating if time is decoded")
    time_range: List[datetime] = Field([], description="Time range for the dataset")
    is_resampled: bool = Field(False, description="Flag indicating if the dataset is resampled")
    resampling_frequency: str = Field('raw', description="Frequency of resampling")
    output_format: str = Field('nc', description="Output format for the dataset")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "url": "https://thredds.met.no/thredds/dodsC/alertness/YOPP_supersite/obs/utqiagvik/utqiagvik_obs_timeSeriesProfileSonde_20180201_20180331.nc",
                "variables": ["ta", "hur", "wdir_refmt"],
                "decoded_time": True,
                "time_range": ["2018-07-01T00:00:00.000000000", "2018-09-30T23:59:00.000000000"],
                "is_resampled": False,
                "resampling_frequency": "raw",
                "output_format": "nc"
            }
        }

class SearchObject(BaseModel):
    # url: AnyUrl = Field('', description="The URL for the CSW endpoint")
    text_entry: str = Field('', description="text entry for the AnyText search")
    keywords_list: List[str] = Field([], description="List of keywords to search for")
    start_time: str = Field('', description="start time for the search")
    end_time: str = Field('', description="end time for the search")
    bbox: str = Field([], description="Map extent for the dataset")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                # "url": "https://nbs.csw.met.no",
                "text_entry": "snentinel",
                "keywords_list": ["S1A", "S1B"],
                "start_time": "2018-07-01T00:00:00.000000000", 
                "end_time": "2018-09-30T23:59:00.000000000",
                "bbox": "0.0,0.0,0.0,0.0" 
            }
        }


class BasketDatasource(BaseModel):
    data: dict = Field(
        default={"": ""},
        example={
            "123e4567-e89b-12d3-a456-426655440003": {
                "title": "Permafrost station KVADEHUKEN II (SN99895)",
                "feature_type": "timeSeriesProfile",
                "resources": {
                    "opendap": ["https://thredds.met.no/thredds/dodsC/arcticdata/frost2netcdf-permafrost/SN99895/2023/SN99895_2023-10-01_2023-10-31_time_resolution_PT1H.nc"]
                },
            },
            "123e4567-e89b-12d3-a456-426655440004": {
                "title": "YOPPsiteMIP",
                "feature_type": "timeSeriesProfile",
                "resources": {
                    "opendap": [
                        "https://thredds.met.no/thredds/dodsC/alertness/YOPP_supersite/obs/utqiagvik/utqiagvik_obs_timeSeriesProfileSonde_20180201_20180331.nc"
                    ]
                },
            },
            "123e4567-e89b-12d3-a456-426655440005": {
                "title": "High resolution sea ice concentration",
                "feature_type": "NA",
                "resources": {
                    "OGC:WMS": [
                        "https://thredds.met.no/thredds/wms/cmems/si-tac/cmems_obs-si_arc_phy-siconc_nrt_L4-auto_P1D_aggregated?service=WMS&version=1.3.0&request=GetCapabilities"
                    ]
                },
            },
            "123e4567-e89b-12d3-a456-426655440006": {
                "title": "S1A EW GRDM",
                "feature_type": "NA",
                "resources": {
                    "OGC:WMS": [
                        "https://nbswms.met.no/thredds/wms_ql/NBS/S1A/2021/05/18/EW/S1A_EW_GRDM_1SDH_20210518T070428_20210518T070534_037939_047A42_65CD.nc?SERVICE=WMS&REQUEST=GetCapabilities"
                    ]
                },
            },
        },
    )
    email: str = Field(default="me@you.web", example="epiesasha@me.com")
    project: Optional[str] = Field(default="METSIS", example="METSIS")
    notebook: Optional[bool] = Field(default=False, example=True)
    notebook: Optional[bool] = Field(default=False, example=True)
    notebooks: Optional[dict] = Field(
        default={"": ""},
        example={
            "UseCase2": {
                "name": "UseCase",
                "purpose": "cool science",
                "resource": "https://raw.githubusercontent.com/UseCase.ipynb",
            }
        },
    )
