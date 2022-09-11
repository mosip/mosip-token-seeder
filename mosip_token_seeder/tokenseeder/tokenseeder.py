import os
import json
import datetime
from logging import Logger
from queue import Queue
from threading import Thread
from sqlalchemy.orm import Session
from sqlalchemy import Table

from .download_handler import DownloadHandler

from mosip_token_seeder.authenticator import MOSIPAuthenticator
from mosip_token_seeder.authenticator.exceptions import AuthenticatorException
from mosip_token_seeder.repository import db_tools
from mosip_token_seeder.repository import AuthTokenRequestDataRepository, AuthTokenRequestRepository


class TokenSeeder(Thread):
    def __init__(self, config, logger : Logger, authenticator : MOSIPAuthenticator, **kwargs):
        self.config = config
        self.logger = logger
        self.authenticator = authenticator
        self.request_id_queue = Queue()
        self.db_engine = db_tools.db_init(config.db.location, password=config.db.password)
        super().__init__(**kwargs)
        self.start()
    
    def run(self):
        while True:
            req_id = self.request_id_queue.get()
            self.logger.info("Req Id: %s", req_id)
            try:
                with Session(self.db_engine) as session:
                    auth_request : AuthTokenRequestRepository = AuthTokenRequestRepository.get_from_session(session, req_id)
                    if auth_request.status == 'submitted':
                        auth_request.status = 'processing'
                        auth_request.update_commit_timestamp(session)
                        data_line_no = auth_request.number_processed + auth_request.number_error
                        total_no = auth_request.number_total
                        while data_line_no < total_no:
                            auth_token_data_entry : AuthTokenRequestDataRepository = AuthTokenRequestDataRepository.get_from_session(session, req_id, data_line_no + 1)
                            if auth_token_data_entry.status == 'submitted':
                                auth_token_data_entry.status = 'processing'
                                auth_token_data_entry.update_commit_timestamp(session)
                                try:
                                    auth_data_output_json = self.authenticator.do_auth(json.loads(auth_token_data_entry.auth_data_input))
                                    self.logger.debug("Auth output json data: %s", auth_data_output_json)
                                    auth_data_output = json.loads(auth_data_output_json)
                                    if 'response' in auth_data_output and auth_data_output['response']['authStatus']:
                                        auth_token_data_entry.auth_data_output = auth_data_output_json
                                        auth_token_data_entry.token = auth_data_output['response']['authToken']
                                        auth_token_data_entry.status = "processed"
                                        auth_request.number_processed += 1
                                    else:
                                        self.logger.error('Authenticator Exception: %s', repr(auth_data_output['errors']))
                                        auth_token_data_entry.status = "error"
                                        if len(auth_data_output['errors']) > 1:
                                            auth_token_data_entry.error_code = 'ATS-REQ-103'
                                            auth_token_data_entry.error_message = ','.join(["%s::%s" % (err['errorCode'], err['errorMessage']) for err in auth_data_output['errors']])
                                        elif len(auth_data_output['errors']) == 1:
                                            auth_token_data_entry.error_code = auth_data_output['errors'][0]['errorCode']
                                            auth_token_data_entry.error_message = auth_data_output['errors'][0]['errorMessage']
                                        else:
                                            auth_token_data_entry.error_code = 'ATS-REQ-100'

                                        auth_request.number_error += 1
                                except AuthenticatorException as ae:
                                    self.logger.error('Authenticator Exception: %s', repr(ae))
                                    auth_token_data_entry.status = "error"
                                    auth_token_data_entry.error_code = ae.error_code
                                    auth_token_data_entry.error_message = ae.error_message
                                    auth_request.number_error += 1
                                except Exception as ex:
                                    self.logger.error('Authenticator Exception: %s', repr(ex))
                                    auth_token_data_entry.status = "error"
                                    auth_token_data_entry.error_code = "ATS-REQ-100"
                                    auth_token_data_entry.error_message = "Unknown exception"
                                    auth_request.number_error += 1
                                auth_token_data_entry.update_timestamp()
                                auth_request.update_timestamp()
                                session.commit()
                            data_line_no = auth_request.number_processed + auth_request.number_error
                    auth_request.status = 'processed' if auth_request.number_error == 0 else 'processed_with_errors'
                    auth_request.update_commit_timestamp(session)
                    output_type = auth_request.output_type
                    delivery_type = auth_request.delivery_type
                    if delivery_type == 'download':
                        DownloadHandler(self.config, self.logger, req_id, output_type, session)
            except Exception as e:
                self.logger.error('Token Seeder Error: %s', repr(e))

    def cleanup_old_entries(self):
        try:
            exp_date_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=float(self.config.cleanup.cleanup_expiry_seconds))
            authtoken_request_table : Table = AuthTokenRequestRepository.__table__
            authtoken_request_data_table : Table = AuthTokenRequestDataRepository.__table__
            self.db_engine.execute(authtoken_request_table.delete().where(authtoken_request_table.c.cr_dtimes < exp_date_time))
            self.db_engine.execute(authtoken_request_data_table.delete().where(authtoken_request_data_table.c.cr_dtimes < exp_date_time))
        except Exception as e:
            self.logger.error('Error deleting old entries from db: %s', repr(e))

        # delete from stored files directory
        self.logger.info('Cleaned up old entries in db. Starting stored_files cleanup')
        try:
            for f in os.listdir(self.config.root.output_stored_files_path):
                f = os.path.join(self.config.root.output_stored_files_path, f)
                if os.stat(f).st_mtime < exp_date_time.timestamp():
                    if os.path.isfile(f):
                        os.remove(f)
        except Exception as e:
            self.logger.error('Error deleting old files: %s', repr(e))
