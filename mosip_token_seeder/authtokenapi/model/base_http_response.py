from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + dt.strftime('.%f')[0:4] + 'Z'

class BaseError(BaseModel):
    errorCode : str
    errorMessage : str

class BaseHttpResponse(BaseModel):
    id : str = 'mosip.token.seeder'
    version : str = '1.0'
    metadata : dict = {}
    responsetime : datetime = datetime.utcnow()
    errors : Optional[List[BaseError]]
    response : Optional[dict]

    class Config:
        json_encoders = {
            datetime: convert_datetime_to_iso_8601_with_z_suffix
        }