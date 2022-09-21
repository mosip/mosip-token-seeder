from pydantic import validator

from mosip_token_seeder.tokenseeder.model import CallbackProperties, CallbackSupportedAuthTypes

from ..exception import MOSIPTokenSeederException

class CallbackProperties(CallbackProperties):
    @validator('odooAuthUrl', pre=True)
    def odoo_auth_url_valid(cls, value, values):
        if values['authType'] == CallbackSupportedAuthTypes.odoo and not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','odooAuthUrl cannot be empty for authType odoo')
        return value

    @validator('username', pre=True)
    def username_valid(cls, value, values):
        if values['authType'] == CallbackSupportedAuthTypes.odoo and not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','username cannot be empty for authType odoo')
        return value

    @validator('database', pre=True)
    def database_valid(cls, value, values):
        if values['authType'] == CallbackSupportedAuthTypes.odoo and not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','database cannot be empty for authType odoo')
        return value

    @validator('staticAuthToken', pre=True)
    def static_bearer_token_valid(cls, value, values):
        if values['authType'] == CallbackSupportedAuthTypes.staticBearer and not value:
            raise MOSIPTokenSeederException('ATS-REQ-102','staticAuthToken cannot be empty for authType staticBearer')
        return value
