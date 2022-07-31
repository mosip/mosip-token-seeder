import json
from typing import Optional
from fastapi import File, Form, Request, UploadFile
from pydantic import Json

from mosip_token_seeder.repository import db_tools

from .service import AuthTokenService
from .exception import MOSIPTokenSeederException
from .model import AuthTokenHttpRequest, AuthTokenCsvHttpRequest, BaseHttpResponse, AuthTokenODKHttpRequest

class AuthTokenApi:
    def __init__(self, app, config, logger, request_id_queue):
        self.authtoken_service = AuthTokenService(config, logger, request_id_queue)

        @app.post(config.root.api_path_prefix + "authtoken/json", response_model=BaseHttpResponse, responses={422:{'model': BaseHttpResponse}})
        async def authtoken_json(request : AuthTokenHttpRequest = None):
            if not request:
                raise MOSIPTokenSeederException('ATS-REQ-102', 'mission request body')
            ##call service to save the details.
            request_identifier = self.authtoken_service.save_authtoken_json(request.request)
            return BaseHttpResponse(response={
                'request_identifier': request_identifier
            })

        @app.post(config.root.api_path_prefix + "authtoken/csv", response_model=BaseHttpResponse, responses={422:{'model': BaseHttpResponse}})
        async def authtoken_csv(request : Json[AuthTokenCsvHttpRequest] = Form(None), csv_file : Optional[UploadFile] = None):
            if not request:
                raise MOSIPTokenSeederException('ATS-REQ-102', 'Missing request body')
            if not csv_file:
                raise MOSIPTokenSeederException('ATS-REQ-102', 'Requires CSV file')
            request_identifier = self.authtoken_service.save_authtoken_csv(request.request, csv_file)
            return BaseHttpResponse(response={
                'request_identifier': request_identifier
            })
        
        @app.post(config.root.api_path_prefix + "authtoken/odk", response_model=BaseHttpResponse, responses={422:{'model': BaseHttpResponse}})
        async def authtoken_odk(request : AuthTokenODKHttpRequest = None):
            # test = AuthTokenODKHttpRequest()
            # print(json.dumps(request))
            # if not request:
            #     raise MOSIPTokenSeederException('ATS-REQ-102', 'Missing request body.')
           
            request_identifier = self.authtoken_service.save_authtoken_odk(request.request)
            return BaseHttpResponse(response={
                'request_identifier': request_identifier
            })
