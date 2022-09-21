import errno
import os
import json
import csv

from sqlalchemy.orm import Session

from .utils import OutputFormatter

from mosip_token_seeder.repository import AuthTokenRequestDataRepository, AuthTokenRequestRepository

class DownloadHandler:
    def __init__(self, config, logger, req_id, output_type, output_format=None, session=None, db_engine=None):
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
                json.dump(
                    json.loads(
                        self.output_formatter_utils.format_output_with_vars(
                            self.output_format,
                            each_request
                        )
                    ),
                    f
                )

            f.write(']')
    
    def write_request_output_to_csv(self):
        if not os.path.isdir(self.config.root.output_stored_files_path):
            os.mkdir(self.config.root.output_stored_files_path)
        with open(os.path.join(self.config.root.output_stored_files_path, self.req_id), 'w+') as f:
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
