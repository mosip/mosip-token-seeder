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
        self.output_format = output_format if output_format else '.output'
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
            request_array = []
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                request_array.append(self.output_formatter_utils.format_output_with_vars(
                    self.output_format,
                    each_request
                ))
            res = self.make_one_callback(request_dict=request_array, auth_res=auth_res)
            self.logger.debug('Response of callback ' + res)
        else:
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                request_dict = self.output_formatter_utils.format_output_with_vars(
                    self.output_format,
                    each_request
                )
                res = self.make_one_callback(request_dict=request_dict, auth_res=auth_res)
                self.logger.debug('Response of callback ' + res)
        self.perform_logout(auth_res=auth_res)

    def call_request_output_with_csv(self):
        with tempfile.TemporaryFile(mode='w+') as f:
            csvwriter = csv.writer(f)
            header_written = True
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                output : dict = self.output_formatter_utils.format_output_with_vars(self.output_format, each_request)
                if not header_written:
                    csvwriter.writerow(output.keys())
                    header_written = True
                csvwriter.writerow([
                    json.dumps(cell) if cell!=None and not isinstance(cell, str) else str(cell) if cell!=None else None
                    for cell in output.values()
                ])
            f.seek(0)
            auth_res = self.perform_auth()
            self.make_one_callback(request_file=f, auth_res=auth_res)
            self.perform_logout(auth_res=auth_res)

    def make_one_callback(self, request_dict=None, request_file=None, auth_res:requests.Response=None):
        request_cookies = {}
        request_headers = {}

        if self.callback_props.authType==CallbackSupportedAuthTypes.odoo:
            request_cookies.update(dict(auth_res.cookies.items()))
        elif self.callback_props.authType==CallbackSupportedAuthTypes.oauth:
            auth_res = self.check_oauth_token_expiry_and_renew(auth_res)
            request_auth_token = auth_res.json()['access_token']
            request_headers['Authorization'] = 'Bearer ' + request_auth_token
        elif self.callback_props.authType==CallbackSupportedAuthTypes.staticBearer:
            request_headers['Authorization'] = 'Bearer ' + self.callback_props.authStaticBearer.token

        request_headers.update(self.callback_props.extraHeaders)
        request_method = getattr(requests, self.callback_props.httpMethod.lower())
        response = request_method(
            self.callback_props.url,
            headers=request_headers,
            cookies=request_cookies,
            json=request_dict,
            files={self.callback_props.requestFileName: request_file} if request_file else {},
            timeout=self.callback_props.timeoutSeconds
        )
        return response.text

    def perform_auth(self):
        auth_res = None
        if self.callback_props.authType==CallbackSupportedAuthTypes.odoo:
            auth_odoo = self.callback_props.authOdoo
            request_headers = auth_odoo.extraHeaders
            auth_res = requests.get(auth_odoo.authUrl, headers=request_headers, json={
                "jsonrpc": "2.0",
                "params": {
                    "db": auth_odoo.database,
                    "login": auth_odoo.username,
                    "password": auth_odoo.password
                }
            })
            self.logger.debug('Auth response for callback ' + auth_res.text)
        elif self.callback_props.authType==CallbackSupportedAuthTypes.oauth:
            auth_oauth = self.callback_props.authOauth
            request_headers = auth_oauth.extraHeaders
            request_data = {}
            if auth_oauth.username:
                request_data['username'] = auth_oauth.username
                request_data['grant_type'] = 'password'
            if auth_oauth.password:
                request_data['password'] = auth_oauth.password
            if auth_oauth.clientId:
                request_data['client_id'] = auth_oauth.clientId
                if not auth_oauth.username:
                    request_data['grant_type'] = 'client_credentials'
            if auth_oauth.clientSecret:
                request_data['client_secret'] = auth_oauth.clientSecret
            auth_res = requests.post(auth_oauth.authUrl, headers=request_headers, data=request_data)
        elif self.callback_props.authType==CallbackSupportedAuthTypes.staticBearer:
            pass
        return auth_res

    def perform_logout(self, auth_res:requests.Response=None):
        logout_res = None
        if self.callback_props.authType==CallbackSupportedAuthTypes.odoo:
            auth_odoo = self.callback_props.authOdoo
            request_headers = auth_odoo.extraHeaders
            request_cookies = dict(auth_res.cookies.items())
            logout_url = auth_odoo.authUrl
            logout_url = logout_url[:-2] if logout_url[-1]=='/' else logout_url
            logout_url = logout_url.split('/')
            logout_url[-1] = 'logout'
            logout_url = '/'.join(logout_url)
            logout_res = requests.get(logout_url, headers=request_headers, cookies=request_cookies)
            self.logger.debug('Logout response for callback ' + logout_res.text)
        elif self.callback_props.authType==CallbackSupportedAuthTypes.oauth:
            pass
        elif self.callback_props.authType==CallbackSupportedAuthTypes.staticBearer:
            pass
        return logout_res

    def check_oauth_token_expiry_and_renew(self, auth_res:requests.Response=None):
        if not auth_res:
            return self.perform_auth()
        request_auth_token = auth_res.json()['access_token']
        if datetime.now().timestamp() >= json.loads(base64.urlsafe_b64decode(request_auth_token.split('.')[1]))['exp']:
            self.logger.info('Oauth Token expired. Regenerating token.')
            return self.perform_auth()
        return auth_res
