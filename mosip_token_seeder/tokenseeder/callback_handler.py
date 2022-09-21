import errno
import os
import json
import csv
import traceback
import requests
import tempfile
import base64

from datetime import datetime

from sqlalchemy.orm import Session

from mosip_token_seeder.repository import AuthTokenRequestDataRepository, AuthTokenRequestRepository

from .utils import OutputFormatter
from .model import CallbackSupportedAuthTypes, CallbackProperties

class CallbackHandler:
    def __init__(self, config, logger, req_id, output_type, callback_props : CallbackProperties, output_format=None, session=None, db_engine=None):
        self.config = config
        self.logger = logger
        self.req_id = req_id
        self.output_type = output_type
        self.output_format = output_format if output_format else '''{
            "vid": "__-vid-__",
            "token": "__-token-__",
            "status": "__-status-__",
            "errorCode": "__-error_code-__",
            "errorMessage": "__-error_message-__"
        }'''
        self.callback_props = callback_props
        self.output_formatter_utils = OutputFormatter(config)
        if session:
            self.session = session
            self.handle()
        else:
            with Session(db_engine) as session:
                self.session = session
                self.handle()

    def handle(self):
        try:
            if self.output_type == 'json':
                self.call_request_output_with_json()
            elif self.output_type == 'csv':
                self.call_request_output_with_csv()
            error_status = None
        except Exception as e:
            error_status = 'error_making_callback_request'
            self.logger.error('Error handling callback request: %s. Stacktrace %s', repr(e), traceback.format_exc())
        if error_status:
            auth_request : AuthTokenRequestRepository = AuthTokenRequestRepository.get_from_session(self.session, self.req_id)
            auth_request.status = error_status
            auth_request.update_commit_timestamp(self.session)

    def call_request_output_with_json(self):
        auth_res = self.perform_auth()
        if self.callback_props.callInBulk:
            request_string = '['
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                if i!=0: request_string+=','
                request_string += self.output_formatter_utils.format_output_with_vars(
                    self.output_format,
                    each_request
                )
            request_string += ']'
            res = self.make_one_callback(request_string=request_string, auth_res=auth_res)
            self.logger.debug('Response of callback ' + res)
        else:
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                request_string = self.output_formatter_utils.format_output_with_vars(
                    self.output_format,
                    each_request
                )
                res = self.make_one_callback(request_string=request_string, auth_res=auth_res)
                self.logger.debug('Response of callback ' + res)

    def call_request_output_with_csv(self):
        with tempfile.TemporaryFile(mode='w+') as f:
            csvwriter = csv.writer(f)
            output_format_dict : dict = json.loads(self.output_format)
            csvwriter.writerow(list(output_format_dict.keys()))
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                csvwriter.writerow([
                    self.output_formatter_utils.format_output_with_vars(
                        json.dumps(cell) if isinstance(cell, dict) else str(cell) if cell!=None else None,
                        each_request
                    ) for cell in output_format_dict.values()
                ])
            f.seek(0)
            auth_res = self.perform_auth()
            self.make_one_callback(request_file=f, auth_res=auth_res)

    def make_one_callback(self, request_string=None, request_file=None, auth_res:requests.Response=None):
        if self.callback_props.authType==CallbackSupportedAuthTypes.odoo:
            request_cookies = dict(auth_res.cookies.items())
            request_headers = {}
            if request_string:
                request_headers['Content-type'] = 'application/json'
        elif self.callback_props.authType==CallbackSupportedAuthTypes.oauth2:
            request_cookies = {}
            auth_res = self.check_oauth2_token_expiry_and_renew(auth_res)
            request_auth_token = auth_res.json()['access_token']
            request_headers = {'Authorization': 'Bearer ' + request_auth_token}
            if request_string:
                request_headers['Content-type'] = 'application/json'
        elif self.callback_props.authType==CallbackSupportedAuthTypes.staticBearer:
            request_cookies = {}
            request_headers = {'Authorization': 'Bearer ' + self.callback_props.staticAuthToken}
            if request_string:
                request_headers['Content-type'] = 'application/json'
        else:
            request_cookies = {}
            request_headers = {}
            if request_string:
                request_headers['Content-type'] = 'application/json'
        request_headers.update(self.callback_props.extraHeaders)
        request_method = getattr(requests, self.callback_props.httpMethod.lower())
        response = request_method(
            self.callback_props.url,
            headers=request_headers,
            cookies=request_cookies,
            data=request_string if request_string else '',
            files={self.callback_props.requestFileName: request_file} if request_file else {},
            timeout=self.callback_props.timeoutSeconds
        )
        return response.text

    def perform_auth(self):
        auth_res = None
        if self.callback_props.authType==CallbackSupportedAuthTypes.odoo:
            request_headers = self.callback_props.extraAuthHeaders
            auth_res = requests.get(self.callback_props.odooAuthUrl, headers=request_headers, json={
                "jsonrpc": "2.0",
                "params": {
                    "db": self.callback_props.database,
                    "login": self.callback_props.username,
                    "password": self.callback_props.password
                }
            })
            self.logger.debug('Auth response for callback ' + auth_res.text)
        elif self.callback_props.authType==CallbackSupportedAuthTypes.oauth2:
            request_headers = self.callback_props.extraAuthHeaders
            request_data = {}
            if self.callback_props.username:
                request_data['username']=self.callback_props.username
                request_data['grant_type']='password'
            if self.callback_props.password:
                request_data['password']=self.callback_props.password
            if self.callback_props.clientId:
                request_data['client_id']=self.callback_props.clientId
                if not self.callback_props.username:
                    request_data['grant_type']='client_credentials'
            if self.callback_props.clientSecret:
                request_data['client_secret']=self.callback_props.clientSecret
            auth_res = requests.post(self.callback_props.oauth2TokenUrl, headers=request_headers, data=request_data)
        elif self.callback_props.authType==CallbackSupportedAuthTypes.staticBearer:
            pass
        return auth_res

    def check_oauth2_token_expiry_and_renew(self, auth_res:requests.Response=None):
        if not auth_res:
            return self.perform_auth()
        request_auth_token = auth_res.json()['access_token']
        if datetime.now().timestamp() >= json.loads(base64.urlsafe_b64decode(request_auth_token.split('.')[1]))['exp']:
            self.logger.info('Oauth2 Token expired. Regenerating token.')
            return self.perform_auth()
        return auth_res
