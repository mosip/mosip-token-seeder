from .model import BaseHttpResponse, MapperFields

class AuthFieldsApi:
    def __init__(self, app, config, logger):
        @app.get(config.root.api_path_prefix + "authtoken/authfields", response_model=BaseHttpResponse)
        def get_auth_fields():
            return BaseHttpResponse(version=config.root.version, response={
                'authfields': list(MapperFields.__fields__.keys())
            })