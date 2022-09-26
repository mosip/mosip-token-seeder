import json

from datetime import datetime
from logging import Logger
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from ..model import BaseHttpResponse, BaseError
from . import MOSIPTokenSeederException, MOSIPTokenSeederNoException

class RequestValidationErrorHandler:
    def __init__(self, app : FastAPI, config, logger : Logger):
        self.config = config
        self.logger = logger
        @app.exception_handler(MOSIPTokenSeederException)
        async def tokenseeder_exception_handler(request, exc):
            self.logger.error('Handling exception: %s' % repr(exc))
            if isinstance(exc, MOSIPTokenSeederNoException):
                code = exc.error_code
                message = exc.error_message
                status_code = exc.return_status_code
                response = exc.response
            else:
                code = exc.error_code
                message = exc.error_message
                status_code = 400
                response = None
            res = BaseHttpResponse(
                version=self.config.root.version,
                errors=[
                    BaseError(
                        errorCode=code,
                        errorMessage=message
                    )
                ],
                response=response
            )
            res_dict = json.loads(res.json())
            return JSONResponse(content=res_dict, status_code=status_code)
        
        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc : RequestValidationError):
            self.logger.error('Handling exception: %s' % repr(exc))
            errors = []
            for err in exc.errors():
                errors.append(BaseError(
                    errorCode='ATS-REQ-102',
                    errorMessage='%s. %s. %s' % ('->'.join([str(i) for i in err['loc']]), str(err['type']), str(err['msg']))
                ))
            res = BaseHttpResponse(
                version=self.config.root.version,
                errors=errors,
                response=None
            )
            res_dict = json.loads(res.json())
            return JSONResponse(content=res_dict, status_code=422)
        
        @app.exception_handler(Exception)
        async def unknown_exception_handler(request, exc):
            self.logger.error('Handling exception: %s' % repr(exc))
            l = str(exc).split('::')
            if len(l)>1:
                code = l[0]
                message = l[1]
            else:
                code = 'ATS-REQ-100'
                message = l[0]
            res = BaseHttpResponse(
                version=self.config.root.version,
                errors=[
                    BaseError(
                        errorCode=code,
                        errorMessage=message
                    )
                ],
                response=None
            )
            status_code=500
            res_dict = json.loads(res.json())
            return JSONResponse(content=res_dict, status_code=status_code)
