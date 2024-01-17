import base64
import json
import logging
import sys
import traceback

from cryptography.hazmat.primitives import hashes

from .model import DemographicsModel
from .exceptions import AuthenticatorException, Errors

class MOSIPAuthenticator:

    def __init__(self, config_obj, logger=None, **kwargs ):
        if not logger:
            self.logger = self._init_logger(config_obj.logging.log_file_path)
        else:
            self.logger = logger

        self.auth_api_url = config_obj.mosip_auth_server.ida_auth_url

        self.partner_id = str(config_obj.mosip_auth.partner_id)
        self.psut_hash_algo = config_obj.mosip_auth.psut_hash_algo
        self.skip_auth = config_obj.mosip_auth.skip_auth

    @staticmethod
    def _init_logger(filename):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        fileHandler = logging.FileHandler(filename)
        streamHandler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)
        logger.addHandler(fileHandler)
        return logger
    
    def do_auth(self, auth_req_data : dict):
        vid = auth_req_data.pop('vid')
        
        self.logger.info('Received Auth Request.')
        try:
            if not self.skip_auth:
                demographic_data = DemographicsModel(**auth_req_data)
                # call {self.auth_api_url}/{vid} API to get data

                # compare demographic_data with this API Response

            # generate token using this
            token = self.generate_psut(vid, self.partner_id, self.psut_hash_algo)

            # return response in form of
            return json.dumps({
                "response": {
                    "authStatus": True,
                    "authToken": token,
                },
                "errors": [
                    {
                        "errorCode": "",
                        "errorMessage": "",
                    }
                ]
            })
        except:
            exp = traceback.format_exc()
            self.logger.error('Error Processing Auth Request. Error Message: {}'.format(exp))
            raise AuthenticatorException(Errors.AUT_BAS_001.name, Errors.AUT_BAS_001.value)

    def generate_psut(self, vid : str, partner_id: str, hash_algo: str):
        hash_algo = getattr(hashes, hash_algo)()
        digest = hashes.Hash(hash_algo)
        digest.update(f'{vid}{partner_id}'.encode(encoding="utf-8"))
        return base64.urlsafe_b64encode(digest.finalize()).rstrip("=")

