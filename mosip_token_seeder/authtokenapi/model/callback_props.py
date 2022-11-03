from typing import Optional

from pydantic import validator

from mosip_token_seeder.tokenseeder.model import CallbackSupportedAuthTypes, CallbackProperties, CallbackAuthTypeOauth, CallbackAuthTypeOdoo, CallbackAuthTypeStaticBearer

from ..exception import MOSIPTokenSeederException

class CallbackAuthTypeOdoo(CallbackAuthTypeOdoo):
    @validator('authUrl', pre=True, always=True)
    def auth_url_valid(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-031','authUrl in authOdoo, cannot be empty for authType odoo')
        return value

    @validator('username', pre=True, always=True)
    def username_valid(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-032','username in authOdoo, cannot be empty for authType odoo')
        return value

    @validator('database', pre=True, always=True)
    def password_valid(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-033','database in authOdoo, cannot be empty for authType odoo')
        return value

class CallbackAuthTypeOauth(CallbackAuthTypeOauth):
    # perform any additional validations here.
    pass

class CallbackAuthTypeStaticBearer(CallbackAuthTypeStaticBearer):
    @validator('token', pre=True)
    def token_valid(cls, value):
        if not value:
            raise MOSIPTokenSeederException('ATS-REQ-034','token in authStaticBearer cannot be empty for authType staticBearer')
        return value

class CallbackProperties(CallbackProperties):
    authOdoo: Optional[CallbackAuthTypeOdoo]
    authOauth: Optional[CallbackAuthTypeOauth]
    authStaticBearer: Optional[CallbackAuthTypeStaticBearer]

    @validator('authType', pre=True)
    def auth_type_valid(cls, value):
        try:
            CallbackSupportedAuthTypes(value)
        except ValueError as ve:
            raise MOSIPTokenSeederException('ATS-REQ-027','unsupported authType in CallbackProperties')
        return value

    @validator('authOdoo', pre=True, always=True)
    def auth_odoo_valid(cls, value, values):
        if values['authType'] == CallbackSupportedAuthTypes.odoo and not value:
            raise MOSIPTokenSeederException('ATS-REQ-028','authOdoo cannot be empty for authType odoo')
        return value

    @validator('authOauth', pre=True, always=True)
    def auth_oauth_valid(cls, value, values):
        if values['authType'] == CallbackSupportedAuthTypes.oauth and not value:
            raise MOSIPTokenSeederException('ATS-REQ-029','authOauth cannot be empty for authType oauth')
        return value

    @validator('authStaticBearer', pre=True, always=True)
    def auth_static_valid(cls, value, values):
        if values['authType'] == CallbackSupportedAuthTypes.staticBearer and not value:
            raise MOSIPTokenSeederException('ATS-REQ-030','authStaticBearer cannot be empty for authType staticBearer')
        return value
