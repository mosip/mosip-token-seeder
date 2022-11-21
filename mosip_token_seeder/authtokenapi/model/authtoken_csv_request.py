from typing import Literal, Union
from . import AuthTokenHttpRequest, AuthTokenBaseRequest, MapperFields

class AuthTokenCsvRequestWithHeader(AuthTokenBaseRequest):
    csvDelimiter : str = ','

class AuthTokenCsvHttpRequest(AuthTokenHttpRequest):
    request : AuthTokenCsvRequestWithHeader
