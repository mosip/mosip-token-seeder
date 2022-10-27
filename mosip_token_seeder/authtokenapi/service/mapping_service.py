import json

from datetime import datetime
from typing import Union

from sqlalchemy import true

from ..model import MapperFields, AuthTokenBaseModel

class MappingService:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def validate_auth_data(self, authdata : dict, mapping: MapperFields, language):
        #"." is used to identify if the target auth_data is having any nested json.
        #for eg. if vid is inside a json object qrcodedata the mapping definition could be qrcodedata.vid

        final_dict = {}

        authdata_vid = self.extract_nested_value(mapping.vid, authdata)
        if not authdata_vid:
            return None, 'ATS-REQ-009', 'vid or its mapping not present'
        # if len(authdata_vid) <= 16 and len(authdata_vid) >= 19:
        #     return None, 'ATS-REQ-002', 'invalid vid construct'
        final_dict['vid'] = authdata_vid

        name_arr = []
        name_present = False
        for name_var in mapping.name:
            authdata_name_var = self.extract_nested_value(name_var, authdata)
            if authdata_name_var is not None:
                name_present = True
            if authdata_name_var:
                name_arr.append(authdata_name_var)
        if not name_present:
            return None, 'ATS-REQ-010', 'name or its mapping not present'
        if len(name_arr) == 0:
            return None, 'ATS-REQ-003', 'name is not provided'
        final_dict['name'] = [{'language':language,'value': self.config.root.name_delimiter.join(name_arr)}]

        authdata_gender = self.extract_nested_value(mapping.gender, authdata)
        if authdata_gender is None:
            return None, 'ATS-REQ-011', 'gender or its mapping not present'
        elif len(authdata_gender) == 0:
            return None, 'ATS-REQ-004', 'gender is empty'
        final_dict['gender'] = [{'language':language,'value': authdata_gender}]

        authdata_dob = self.extract_nested_value(mapping.dob, authdata)
        if authdata_dob is None:
            return None, 'ATS-REQ-012', 'dateOfBirth or its mapping not present'
        if len(authdata_dob) == 0:
            return False, 'ATS-REQ-006', 'date of birth is empty'
        # try:
        #     if bool(datetime.strptime(authdata_dob, '%Y/%m/%d')) == False:
        #         return None, 'ATS-REQ-007', 'not a valid date format for date of birth'
        # except ValueError:
        #     return None, 'ATS-REQ-007', 'not a valid date format for date of birth'
        final_dict['dob'] = authdata_dob

        authdata_phone = self.extract_nested_value(mapping.phoneNumber, authdata)
        if authdata_phone:
            final_dict['phoneNumber'] = authdata_phone

        authdata_email = self.extract_nested_value(mapping.emailId, authdata)
        if authdata_email:
            final_dict['emailId'] = authdata_email

        addr_arr = []
        addr_present = False
        for addr in mapping.fullAddress:
            addr_val  = self.extract_nested_value(addr, authdata)
            if addr_val is not None:
                addr_present = True
            if addr_val:
                addr_arr.append(addr_val)
        if not addr_present:
            return None, 'ATS-REQ-015', 'fullAddress or its mapping not present'
        if len(addr_arr) == 0:
            return False, 'ATS-REQ-008', 'address is empty'
        final_dict['fullAddress'] = [{'language':language,'value': self.config.root.full_address_delimiter.join(addr_arr)}]

        return AuthTokenBaseModel(**final_dict),'', ''

    def extract_nested_value(self, mapping_field, authdata : dict):
        # this method traverses the nested json to find the value based on the nested field provided
        part_value = authdata
        for part in mapping_field.split("."):
            if not (isinstance(part_value, dict) and part in part_value):
                return None
            part_value = part_value[part]
        return part_value
