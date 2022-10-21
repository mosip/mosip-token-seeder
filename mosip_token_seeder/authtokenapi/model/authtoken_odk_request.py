from pydantic import BaseModel, validator
from typing import List, Optional

from . import AuthTokenHttpRequest

from . import AuthTokenBaseRequest

from ..exception import MOSIPTokenSeederException
from . import MapperFields

supported_output_types = ['json','csv']
supported_delivery_types = ['download']


class ODKConfig(BaseModel):
    odataurl : Optional[str]
    baseurl : str
    version : str = "v1"
    projectid : Optional[str]
    formid : Optional[str]
    email : str
    password : str
    startdate : Optional[str]
    enddate : Optional[str]


class AuthTokenODKRequest(AuthTokenBaseRequest):
    odkconfig : ODKConfig

    # @validator('odkconfig')
    # def auth_data_validate(cls, value):
    #     if not value:
    #         raise MOSIPTokenSeederException('ATS-REQ-102','authdata missing')
    #     return value
    # pass

class AuthTokenODKHttpRequest(AuthTokenHttpRequest):
    request : AuthTokenODKRequest
    