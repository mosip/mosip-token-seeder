import array
import datetime
import json


from pydantic import BaseModel
from typing import List, Optional

from mosip_token_seeder.authenticator.model import DemographicsModel

# {
#     "vid": "2014391641351279",
#     "name": [{"language":"eng", "value": "EMANASAR-TEST-6"}],
#     "gender": [{"language":"eng", "value": "Male"}],
#     "dob": "1976/01/01",
#     "phoneNumber": "8360334018",
#     "emailId": "PRASHANT.SINGH@IIITB.AC.IN",
#     "fullAddress": [{"language":"eng", "value": "BANGALORE, Electronics City, Bengaluru, Karnataka, 560016"}]
# }


class AuthTokenBaseModel(DemographicsModel):
    vid: Optional[str]


class MapperFields(BaseModel):
    vid: str = 'vid'
    name: List[str] = ['name']
    gender: str = 'gender'
    dob: str = 'dob'
    phoneNumber: str = 'phoneNumber'
    emailId: str = 'emailId'
    fullAddress: List[str] = ['fullAddress']


class MapperFieldIndices(BaseModel):
    vid: int = 0
    name: List[int] = [1]
    gender: int = 2
    dob: int = 3
    phoneNumber: int = 4
    emailId: int = 5
    fullAddress: List[int] = [6]
