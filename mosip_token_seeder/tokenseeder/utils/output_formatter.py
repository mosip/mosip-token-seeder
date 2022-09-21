import json

from dynaconf import Dynaconf

from mosip_token_seeder.repository import AuthTokenRequestDataRepository

from . import NestedJsonUtils

class OutputFormatter:
    def __init__(self, config : Dynaconf):
        self.config = config
        self.nested_json_utils = NestedJsonUtils()

    def get_item_for_output(self, var_name : str, each_request : AuthTokenRequestDataRepository):
        if var_name=='vid':
            if each_request.auth_data_input:
                each_vid = json.loads(each_request.auth_data_input)['vid']
            else:
                each_received = json.loads(each_request.auth_data_received)
                each_vid = each_received['vid'] if 'vid' in each_received else None
            return each_vid
        elif var_name=='status':
            return each_request.status
        elif var_name=='token':
            return each_request.token
        elif var_name=='error_code':
            return each_request.error_code
        elif var_name=='error_message':
            return each_request.error_message
        else:
            if each_request.auth_data_received:
                each_input_received = json.loads(each_request.auth_data_received)
                return self.nested_json_utils.extract_nested_value(var_name, each_input_received)
            else:
                return None

    def format_output_with_vars(self, output_format, request : AuthTokenRequestDataRepository):
        if output_format=='' or output_format==None:
            return None
        output = str(output_format)
        while True:
            find_index = output.find(self.config.root.output_format_var_starts)
            if find_index == -1: break
            find_end_index = output.find(self.config.root.output_format_var_ends)
            if find_end_index == -1: break
            var_name = output[
                find_index+
                len(self.config.root.output_format_var_starts):
                find_end_index
            ]
            find_length = len(self.config.root.output_format_var_starts)+len(var_name)+len(self.config.root.output_format_var_ends)
            var_value = self.get_item_for_output(var_name, request)
            if not var_value:
                var_value = ''
            if find_index != 0 and output[find_index-1] == '"' and output[find_index+find_length] == '"' and not isinstance(var_value, str):
                find_index-=1
                find_length+=2
            try:
                var_value = json.dumps(var_value) if not isinstance(var_value, str) else var_value
                output = output[:find_index] + var_value + output[find_index+find_length:]
            except:
                var_value = str(var_value)
                output = output[:find_index] + var_value + output[find_index+find_length:]
        return output
