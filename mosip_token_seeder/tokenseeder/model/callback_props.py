from enum import Enum
from pydantic import BaseModel, AnyUrl
from typing import Optional

class CallbackSupportedAuthTypes(Enum):
    none = 'none'
    odoo = 'odoo'
    oauth2 = 'oauth2'
    staticBearer = 'staticBearer'

class CallbackProperties(BaseModel):
    url : AnyUrl
    httpMethod : str = 'POST'
    extraHeaders : dict = {}
    timeoutSeconds : int = 10
    callInBulk : bool = False
    requestFileName : str = ""
    authType : CallbackSupportedAuthTypes = CallbackSupportedAuthTypes.none
    extraAuthHeaders : dict = {}
    staticAuthToken : str = ""
    database : str = ""
    odooAuthUrl : Optional[AnyUrl]
    oauth2TokenUrl : Optional[AnyUrl]
    username : str = ""
    password : str = ""
    clientId : str = ""
    clientSecret : str = ""
