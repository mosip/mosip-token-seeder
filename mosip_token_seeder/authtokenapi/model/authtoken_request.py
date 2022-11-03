import json

from pydantic import BaseModel, validator
from typing import List, Optional

from ..exception import MOSIPTokenSeederException
from . import MapperFields, CallbackProperties

supported_output_types = ['json','csv']
supported_delivery_types = ['download','callback']

class AuthTokenBaseRequest(BaseModel):
    output: str
    deliverytype: str
    mapping: MapperFields = MapperFields()
    lang: Optional[str]
    outputFormat : Optional[str] = ''
    callbackProperties : Optional[CallbackProperties]

    @validator('output', pre=True)
    def output_valid(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','invalid input. output type is not mentioned')
        if value not in supported_output_types:
            raise MOSIPTokenSeederException('ATS-REQ-102','invalid input. output type is not supported')
        return value
    
    @validator('deliverytype', pre=True)
    def delivery_valid(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','invalid input. delivery type is not mentioned')
        if value not in supported_delivery_types:
            raise MOSIPTokenSeederException('ATS-REQ-102','invalid input. delivery type is not supported')
        return value

    @validator('outputFormat', pre=True)
    def output_format_valid(cls, value, values):
        if value:
            value_dict = None
            try:
                value_dict = json.loads(value)
            except:
                raise MOSIPTokenSeederException('ATS-REQ-103','outputFormat is not a valid json string')
            if isinstance(value_dict, list) and 'output' in values and values['output'] == 'csv':
                raise MOSIPTokenSeederException('ATS-REQ-104','For csv output, outputFormat cannot be list. Has to be json')
        return value

    @validator('callbackProperties', pre=True, always=True)
    def callback_prop_valid(cls, value, values):
        if values['deliverytype'] == 'callback' and not value:
            raise MOSIPTokenSeederException('ATS-REQ-024','callbackProperties cannot be empty for deliverytype callback')
        if values['deliverytype'] != 'callback':
            return None
        if values['output'] == 'csv' and not value['requestFileName']:
            raise MOSIPTokenSeederException('ATS-REQ-025','requestFileName is not valid in callbackProperties')
        if values['output'] == 'csv' and not value['callInBulk']:
            raise MOSIPTokenSeederException('ATS-REQ-026','callInBulk cannot be false for csv output')
        return value

class AuthTokenRequest(AuthTokenBaseRequest):
    authdata: Optional[List[dict]]

    @validator('authdata', always=True)
    def auth_data_validate(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','invalid input. authdata missing')
        return value
