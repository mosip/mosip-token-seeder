import json

from pydantic import BaseModel, validator
from typing import List, Optional

from ..exception import MOSIPTokenSeederException
from . import MapperFields

supported_output_types = ['json','csv']
supported_delivery_types = ['download','sync','callback']

class AuthTokenBaseRequest(BaseModel):
    output: str
    deliverytype: str
    mapping: MapperFields = MapperFields()
    lang: Optional[str]
    outputFormat : Optional[str] = ''

    @validator('output', pre=True)
    def output_valid(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','output type is not mentioned')
        if value not in supported_output_types:
            raise MOSIPTokenSeederException('ATS-REQ-102','output type is not supported')
        return value
    
    @validator('deliverytype', pre=True)
    def delivery_valid(cls, value, values):
        if value == 'sync':
            if cls is not AuthTokenRequest:
                raise MOSIPTokenSeederException('ATS-REQ-102','Only json input supported for sync delivery')
            if values['output']!='json':
                raise MOSIPTokenSeederException('ATS-REQ-102','Only json output supported for sync delivery')
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','delivery type is not mentioned')
        if value not in supported_delivery_types:
            raise MOSIPTokenSeederException('ATS-REQ-102','delivery type is not supported')
        return value

    @validator('outputFormat', pre=True)
    def output_format_valid(cls, value):
        if value:
            try: json.loads(value)
            except: raise MOSIPTokenSeederException('ATS-REQ-102','outputFormat is not a valid json string')
        return value

class AuthTokenRequest(AuthTokenBaseRequest):
    authdata: Optional[List[dict]]

    @validator('authdata')
    def auth_data_validate(cls, value, values):
        if values['deliverytype'] == 'sync':
            if len(value)>1:
                raise MOSIPTokenSeederException('ATS-REQ-102','Only one authdata entry can be supplied for sync delivery')
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','authdata missing')
        return value
