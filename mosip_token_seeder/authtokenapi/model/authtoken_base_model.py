import array
import datetime
import json


from pydantic import BaseModel
from typing import List, Optional

from mosip_token_seeder.authenticator.model import DemographicsModel

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
