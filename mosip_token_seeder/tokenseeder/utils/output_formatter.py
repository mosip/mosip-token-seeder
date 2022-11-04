import json

from dynaconf import Dynaconf

from mosip_token_seeder.repository import AuthTokenRequestDataRepository

from . import JqUtils

class OutputFormatter:
    def __init__(self, config : Dynaconf):
        self.config = config
        self.jq_utils = JqUtils()

    def format_output_with_vars(self, output_format, request : AuthTokenRequestDataRepository):
        if output_format=='' or output_format==None:
            return None
        vid = None
        if request.auth_data_input:
            vid = json.loads(request.auth_data_input)['vid']
        else:
            each_received = json.loads(request.auth_data_received)
            vid = each_received['vid'] if 'vid' in each_received else None
        return self.jq_utils.eval_single_expr(output_format, {
            'input': json.loads(request.auth_data_received),
            'output': {
                'vid': vid,
                'status': request.status,
                'token': request.token,
                'errorCode': request.error_code,
                'errorMessage': request.error_message
            }
        })
