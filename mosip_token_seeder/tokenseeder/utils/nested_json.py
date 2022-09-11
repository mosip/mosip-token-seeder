class NestedJsonUtils:
    def __init__(self):
        pass

    def extract_nested_value(self, nested_field, data : dict):
        if nested_field in data:
            return data[nested_field]
        # this method traverses the nested json to find the value based on the nested field provided
        part_value = data
        for part in nested_field.split("."):
            if part not in part_value:
                return None
            part_value = part_value[part]
        return part_value

    def whether_nested_field_in(self, nested_field, data : dict):
        if nested_field in data:
            return True
        part_value = data
        for part in nested_field.split("."):
            if part not in part_value:
                return False
            part_value = part_value[part]
        return True
