from enum import Enum
from pydantic import BaseModel, AnyUrl
from typing import Optional

class CallbackSupportedAuthTypes(Enum):
    none = 'none'
    odoo = 'odoo'
    oauth = 'oauth'
    staticBearer = 'staticBearer'

class CallbackAuthTypeOdoo(BaseModel):
    authUrl: Optional[AnyUrl]
    database: str
    username: str
    password: str
    extraHeaders: Optional[dict]

class CallbackAuthTypeOauth(BaseModel):
    authUrl: Optional[AnyUrl]
    username : str = ""
    password : str = ""
    clientId : str = ""
    clientSecret : str = ""
    extraHeaders: Optional[dict]

class CallbackAuthTypeStaticBearer(BaseModel):
    token: str

class CallbackProperties(BaseModel):
    url : AnyUrl
    httpMethod : str = 'POST'
    extraHeaders : dict = {}
    timeoutSeconds : int = 10
    callInBulk : bool = False
    requestFileName : str = ""
    authType : CallbackSupportedAuthTypes = CallbackSupportedAuthTypes.none
    authOdoo: Optional[CallbackAuthTypeOdoo]
    authOauth: Optional[CallbackAuthTypeOauth]
    authStaticBearer: Optional[CallbackAuthTypeStaticBearer]
