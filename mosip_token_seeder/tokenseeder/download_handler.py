import errno
import os
import json
import csv

from sqlalchemy.orm import Session

from mosip_token_seeder.repository import AuthTokenRequestDataRepository, AuthTokenRequestRepository

class DownloadHandler:
    def __init__(self, config, logger, req_id, output_type, session=None, db_engine=None):
        self.config = config
        self.logger = logger
        self.req_id = req_id
        self.output_type = output_type
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
                self.write_request_output_to_json()
            elif self.output_type == 'csv':
                self.write_request_output_to_csv()
            error_status = None
        except PermissionError as e:
            error_status = 'error_creating_download_disk_permission_error'
            self.logger.error('Error handling file: %s', repr(e))
        except IOError as e:
            if e.errno == errno.ENOSPC:
                error_status = 'error_creating_download_disk_space_error'
            else:
                error_status = 'error_creating_download_unknown_io_error'
            self.logger.error('Error handling file: %s', repr(e))
        except Exception as e:
            error_status = 'error_creating_download_unknown_exception'
            self.logger.error('Error handling file: %s', repr(e))
        if error_status:
            auth_request : AuthTokenRequestRepository = AuthTokenRequestRepository.get_from_session(self.session, self.req_id)
            auth_request.status = error_status
            auth_request.update_commit_timestamp(self.session)
    
    def write_request_output_to_json(self):
        if not os.path.isdir(self.config.root.output_stored_files_path):
            os.mkdir(self.config.root.output_stored_files_path)
        with open(os.path.join(self.config.root.output_stored_files_path, self.req_id), 'w+') as f:
            f.write('[')
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                f.write(',') if i!=0 else None
                each_err = each_request.error_code
                each_err_message = each_request.error_message
                if each_request.auth_data_input:
                    each_vid = json.loads(each_request.auth_data_input)['vid']
                else:
                    each_received = json.loads(each_request.auth_data_received)
                    each_vid = each_received['vid'] if 'vid' in each_received else None
                json.dump({
                    'vid': each_vid,
                    'token': each_request.token,
                    'status': each_request.status,
                    'errorCode': each_err if each_err else None,
                    'errorMessage': each_err_message if each_err_message else None,
                },f)
            f.write(']')
    
    def write_request_output_to_csv(self):
        if not os.path.isdir(self.config.root.output_stored_files_path):
            os.mkdir(self.config.root.output_stored_files_path)
        with open(os.path.join(self.config.root.output_stored_files_path, self.req_id), 'w+') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(['vid', 'token', 'status', 'errorCode', 'errorMessage'])
            for i, each_request in enumerate(AuthTokenRequestDataRepository.get_all_from_session(self.session, self.req_id)):
                each_err = each_request.error_code
                each_err_message = each_request.error_message
                if each_request.auth_data_input:
                    each_vid = json.loads(each_request.auth_data_input)['vid']
                else:
                    each_received = json.loads(each_request.auth_data_received)
                    each_vid = each_received['vid'] if 'vid' in each_received else None
                csvwriter.writerow([
                    each_vid,
                    each_request.token,
                    each_request.status,
                    each_err if each_err else None,
                    each_err_message if each_err_message else None,
                ])
