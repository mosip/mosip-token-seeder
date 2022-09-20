import http
import json

from mosip_token_seeder.authtokenapi.exception.mosip_token_seeder_exception import MOSIPTokenSeederException, MOSIPTokenSeederNoException
from mosip_token_seeder.authtokenapi.model.authtoken_odk_request import ODKConfig


class ODKPullService:
    def __init__(self, logger):
        self.logger = logger

    def odk_pull(self, config: ODKConfig):

        if config.baseurl is None or not len(config.baseurl):
            raise MOSIPTokenSeederException(
                'ATS-REQ-18', 'no odk baseurl provided')

        if config.email is None or not len(config.email):
            raise MOSIPTokenSeederException('ATS-REQ-19', 'no email provided')

        if config.password is None or not len(config.password):
            raise MOSIPTokenSeederException(
                'ATS-REQ-20', 'no password provided')

        credentials = {
            "email": config.email,
            "password": config.password
        }
        auth_url = 'https://{domain}/{version}/sessions'
        domain = config.baseurl
        version = config.version if config.version is not None and len(
            config.version) else 'v1'

        connection = http.client.HTTPSConnection(domain)
        headers = {'Content-type': 'application/json'}
        connection.request(method='POST', url=auth_url.format(
            domain=domain, version=version), body=json.dumps(credentials), headers=headers)
        response = connection.getresponse()
        response_json_string = response.read().decode()
        auth_data = json.loads(response_json_string)
        token = auth_data['token']
        if config.odataurl is not None and len(config.odataurl):
            odata_url = config.odataurl + "/Submissions"
        else:
            if config.projectid is None or not len(config.projectid):
                raise MOSIPTokenSeederException(
                    'ATS-REQ-21', 'no odk project id provided')

            if config.formid is None or not len(config.formid):
                raise MOSIPTokenSeederException(
                    'ATS-REQ-22', 'no odk form id provided')

        service_url = 'https://{domain}/{version}/projects/{projectid}/forms/{formid}.svc/Submissions'
        service_url = service_url.format(domain=domain, version=version,
                           projectid=config.projectid, formid=config.formid)
        odata_url = service_url
        if config.startdate is not None and len(config.startdate) and config.enddate is not None and len(config.enddate):
            filter = '?$filter=__system/submissionDate%20gt%20' + config.startdate + \
                '%20and%20__system/submissionDate%20lt%20' + config.enddate
            odata_url = odata_url + filter

        
        
        auth_header = {'Authorization': 'Bearer ' + token}
        connection.request(method="GET", url=odata_url, headers=auth_header)
        response = connection.getresponse()
        response_json_string = response.read().decode()
        submissions = json.loads(response_json_string)
        if 'value' in submissions:
            if submissions['value'] is None  or  len(submissions['value']) == 0 :
                raise MOSIPTokenSeederException(
                    'ATS-REQ-23', 'no submissions found for odk pull')     
            return submissions['value']
        else:
            raise MOSIPTokenSeederException(
                'ATS-REQ-23', 'no submissions found for odk pull')
