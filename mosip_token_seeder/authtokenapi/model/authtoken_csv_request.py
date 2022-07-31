from typing import Literal, Union
from . import AuthTokenHttpRequest, AuthTokenBaseRequest, MapperFields, MapperFieldIndices

class AuthTokenCsvRequestWithHeader(AuthTokenBaseRequest):
    # Enabled csv expected with header by default.
    # csvWithHeader : Literal[True] = True
    mapping : MapperFields = MapperFields()
    csvDelimiter : str = ','

class AuthTokenCsvRequestWithoutHeader(AuthTokenBaseRequest):
    # This class is ignored as of now
    csvWithHeader : Literal[False]
    mapping : MapperFieldIndices = MapperFieldIndices()
    csvDelimiter : str = ','

AuthTokenCsvRequest = Union[AuthTokenCsvRequestWithHeader, AuthTokenCsvRequestWithoutHeader]

class AuthTokenCsvHttpRequest(AuthTokenHttpRequest):
    request : AuthTokenCsvRequestWithHeader
