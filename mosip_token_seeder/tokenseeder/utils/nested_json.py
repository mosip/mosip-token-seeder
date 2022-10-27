import re

class NestedJsonUtils:
    def __init__(self):
        pass

    def extract_nested_value(self, nested_field, data : dict):
        if nested_field in data:
            return data[nested_field]
        # this method traverses the nested json to find the value based on the nested field provided
        part_value = data
        for part in nested_field.split("."):
            part_value = self.get_nested_field_list_item(part_value, part)
            if part_value is None:
                return None
        return part_value

    def get_nested_field_list_item(self, part_value, part):
        if part_value is None:
            return None
        regex_res = re.match(r'(.*)\[(\d+)\]', part)
        if regex_res:
            part = regex_res.group(1)
            arr_index = int(regex_res.group(2))
            part_value = self.get_nested_field_list_item(part_value, part)
            if (not isinstance(part_value, list)) or arr_index >= len(part_value):
                return None
            return part_value[arr_index]
        if not (isinstance(part_value, dict) and part in part_value):
            return None
        return part_value[part]
