import json

from datetime import datetime
from typing import Union

from sqlalchemy import true
from ..model import MapperFieldIndices, MapperFields, AuthTokenBaseModel

class MappingService:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def validate_auth_data(self, authdata, mapping: Union[MapperFields, MapperFieldIndices], language):
        if isinstance(mapping, MapperFields):
            return self.validate_auth_data_json_mapper(authdata, mapping, language)
        elif isinstance(mapping, MapperFieldIndices):
            return self.validate_auth_data_indices_mapper(authdata, mapping, language)

    def validate_auth_data_json_mapper(self, authdata : dict, mapping: MapperFields, language):

        #"." is used to identify if the target auth_data is having any nested json.        
        #for eg. if vid is inside a json object qrcodedata the mapping definition could be qrcodedata.vid

        final_dict = {}
        
        if mapping.vid.find('.') !=-1:                                                  
            final_dict['vid'] = self.extract_nested_value(mapping.vid, authdata, mapping)    
        else :    
            if mapping.vid not in authdata:
                return None, 'ATS-REQ-009', 'vid or its mapping not present'
            # if len(authdata[mapping.vid]) <= 16 and len(authdata[mapping.vid]) >= 19:
            #     return None, 'ATS-REQ-002'
            final_dict['vid'] = authdata[mapping.vid]

        name_arr = []
        for name_var in mapping.name:
            if name_var.find('.') != -1 :                                               
                name_val = self.extract_nested_value(name_var, authdata, mapping)
                if name_val:
                    name_arr.append(name_val )
            else:
                if name_var not in authdata:
                    return None, 'ATS-REQ-010', 'name or its mapping not present'
                if len(authdata[name_var]) == 0:
                    return None, 'ATS-REQ-003', 'name is not provided'
                name_arr.append(authdata[name_var])

        final_dict['name'] = [{'language':language,'value': self.config.root.name_delimiter.join(name_arr)}]


        if mapping.gender.find('.') != -1 :                                             
            final_dict['gender'] = [{'language':language,'value': self.extract_nested_value(mapping.gender, authdata, mapping) }]   
        else :
            if mapping.gender not in authdata:
                return None, 'ATS-REQ-011', 'gender or its mapping not present'
            if len(authdata[mapping.gender]) == 0:
                return None, 'ATS-REQ-004', 'gender is empty'
            # if len(authdata[mapping.gender]) > 256:
            #     return None, 'ATS-REQ-003'
            # if authdata[mapping.gender].lower() not in ['male','female','others']:
            #     return None, 'ATS-REQ-005'
            final_dict['gender'] = [{'language':language,'value': authdata[mapping.gender]}]

        if mapping.dob.find('.') != -1 :                                                
            final_dict['dob'] = self.extract_nested_value(mapping.dob, authdata, mapping) 
        else:
            if mapping.dob not in authdata:
                return None, 'ATS-REQ-012', 'dateOfBirth or its mapping not present'
            if len(authdata[mapping.dob]) == 0:
                return False, 'ATS-REQ-006', 'date of birth is empty'
            # try:
            #     if bool(datetime.strptime(authdata[mapping.dob], '%Y/%m/%d')) == False:
            #         return None, 'ATS-REQ-007'
            # except ValueError:
            #     return None, 'ATS-REQ-007'
            final_dict['dob'] = authdata[mapping.dob]
            
        if mapping.phoneNumber.find('.') != -1 : 
            final_dict['phoneNumber'] = self.extract_nested_value(mapping.phoneNumber, authdata, mapping) 
        else:
            if mapping.phoneNumber in authdata:
                # return None, 'ATS-REQ-013' // removed phone validation
                final_dict['phoneNumber'] = authdata[mapping.phoneNumber]

        if mapping.emailId.find('.') != -1 :
            final_dict['emailId'] = self.extract_nested_value(mapping.emailId, authdata, mapping) 
        else :
            if mapping.emailId  in authdata:
                # return None, 'ATS-REQ-014' // removed email validation
                final_dict['emailId'] = authdata[mapping.emailId]

        addr_arr = []
        for addr in mapping.fullAddress:
            if addr.find('.') != -1 :
                addr_val  = self.extract_nested_value(addr, authdata, mapping)
                if addr_val:
                    addr_arr.append(addr_val)
            else:
                if addr not in authdata:
                    return None, 'ATS-REQ-015', 'fullAddress or its mapping not present'
                if len(authdata[addr]) == 0:
                    return False, 'ATS-REQ-008', 'address is empty'
                addr_arr.append(authdata[addr])
        final_dict['fullAddress'] = [{'language':language,'value': self.config.root.full_address_delimiter.join(addr_arr)}]

        return AuthTokenBaseModel(**final_dict),""

    def validate_auth_data_indices_mapper(self, authdata : list, mapping: MapperFieldIndices, language):
        final_dict = {}
        len_of_authdata = len(authdata)
        if mapping.vid >= len_of_authdata:
            return None, 'ATS-REQ-009', 'vid or its mapping not present'
        # if len(authdata[mapping.vid]) <= 16 and len(authdata[mapping.vid]) >= 19:
        #     return None, 'ATS-REQ-002'
        final_dict['vid'] = authdata[mapping.vid]

        name_arr = []
        for name_index in mapping.name:
            if name_index >= len_of_authdata:
                return None, 'ATS-REQ-010', 'name or its mapping not present'
            if len(authdata[name_index]) == 0:
                return None, 'ATS-REQ-003', 'name is not provided'
            name_arr.append(authdata[name_index])
        final_dict['name'] = [{'language':language,'value': self.config.root.name_delimiter.join(name_arr)}]

        if mapping.gender >= len_of_authdata:
            return None, 'ATS-REQ-011', 'gender or its mapping not present'
        if len(authdata[mapping.gender]) == 0:
            return None, 'ATS-REQ-004', 'gender is empty'
        # if len(authdata[mapping.gender]) > 256:
        #     return None, 'ATS-REQ-003'
        # if authdata[mapping.gender].lower() not in ['male','female','others']:
        #     return None, 'ATS-REQ-005'
        final_dict['gender'] = [{'language':language,'value': authdata[mapping.gender]}]

        if mapping.dob >= len_of_authdata:
            return None, 'ATS-REQ-012', 'dateOfBirth or its mapping not present'
        if len(authdata[mapping.dob]) == 0:
            return False, 'ATS-REQ-006', 'date of birth is empty'
        # try:
        #     if bool(datetime.strptime(authdata[mapping.dob], '%Y/%m/%d')) == False:
        #         return None, 'ATS-REQ-007'
        # except ValueError:
        #     return None, 'ATS-REQ-007'
        final_dict['dob'] = authdata[mapping.dob]
        
        if mapping.phoneNumber >= len_of_authdata:
            return None, 'ATS-REQ-013', 'phoneNumber or its mapping not present'
        final_dict['phoneNumber'] = authdata[mapping.phoneNumber]

        if mapping.emailId >= len_of_authdata:
            return None, 'ATS-REQ-014', 'emailId or its mapping not present'
        final_dict['emailId'] = authdata[mapping.emailId]

        addr_arr = []
        for addr_index in mapping.fullAddress:
            if addr_index >= len_of_authdata:
                return None, 'ATS-REQ-015', 'fullAddress or its mapping not present'
            if len(authdata[addr_index]) == 0:
                return False, 'ATS-REQ-008', 'address is empty'
            addr_arr.append(authdata[addr_index])
        final_dict['fullAddress'] = [{'language':language,'value': self.config.root.full_address_delimiter.join(addr_arr)}]

        return AuthTokenBaseModel(**final_dict),""

    def extract_nested_value(self, mapping_field, authdata : dict, mapping: MapperFields) :
        # this method traverses the nested json to find the value based on the mapping field provided as per template (refer the api documentation) 
        parts = mapping_field.split(".")
        part_value = authdata[parts[0]]
        part_index = 1
        while part_index < len(parts):
            if part_value and parts[part_index] in part_value:
                part_value = part_value[parts[part_index]]
            else :
                part_value = None
            part_index += 1
        return part_value