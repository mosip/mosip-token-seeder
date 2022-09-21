from datetime import datetime
from pydantic import BaseModel, validator
from typing import List, Optional

from ..exception import MOSIPTokenSeederException

from . import MapperFields

class AuthTokenRequestSync(BaseModel):
    mapping: MapperFields = MapperFields()
    lang: Optional[str]
    authdata: Optional[dict]

class AuthTokenHttpRequestSync(BaseModel):
    id: str
    version: str
    metadata: str
    requesttime: datetime
    request: AuthTokenRequestSync

    @validator('requesttime', pre=True)
    def parse_datetime(cls, value):
        try:
            return datetime.strptime(
                value,
                '%Y-%m-%dT%H:%M:%S.%fZ'
            )
        except:
            raise MOSIPTokenSeederException('ATS-REQ-102','requesttime is not in valid format')