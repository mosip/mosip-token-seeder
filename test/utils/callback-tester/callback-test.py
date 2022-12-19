import os
import json
import jwt
import traceback
from fastapi import FastAPI, Request, Response 
from starlette.datastructures import UploadFile

app = FastAPI()

jwks_client = jwt.PyJWKClient(os.getenv("JWKS_URI","http://keycloak.keycloak/auth/realms/mosip/protocol/openid-connect/certs"))

def log_base_method_call(request: Request):
    print(  "\nThis is request: " + str(request.url) +
            "\nThis is request method: " + str(request.method) +
            "\nThis is request type: " + request.headers.get('content-type', ''))

async def handle_jwt_token(request):
    token = request.headers['authorization'].replace('Bearer ', '')
    try:
        key = jwks_client.get_signing_key_from_jwt(token).key
        jwt_payload_unverified = jwt.decode(token,options={"verify_signature": False})
    except Exception as e:
        print(f"This is jwt unable to fetch payload\n")
        print(f"Error handling jwt: {e.__repr__()}")
        raise e
    print(f"This is jwt payload :\n{json.dumps(jwt_payload_unverified, indent=4)}")
    try:
        jwt_payload = jwt.decode(token,key,algorithms=["RS256"],options={"verify_iss": False, "verify_aud": False})
        print(f"This is jwt Verified\n")
    except Exception as e:
        print(f"This is jwt NOT Verified\n")
        print(f"Error handling jwt: {e.__repr__()}")
        raise e

async def handle_json_payload(request):
    if ("application/json" not in request.headers.get('content-type', '').lower()): raise ValueError()
    request_json = json.dumps(await request.json(), indent=4)
    print(f"This is json payload : \n{request_json}\n")

async def handle_csv_payload(request):
    if ("multipart/form-data" not in request.headers.get('content-type', '').lower()): raise ValueError()
    request_forms = await request.form()
    print(f"This is file input. Payload :\n{request_forms}\n")
    for form in request_forms:
        print(f"Form : {form} --")
        if isinstance(request_forms[form], UploadFile):
            file_data_b = await request_forms[form].read()
            file_data = file_data_b.decode('UTF-8')
            file_name = str(request_forms[form].filename)
            print(f"File Form. Filename: {file_name}. Data:\n\n{file_data}\n")
            try:
                with open(file_name+'.csv','wb') as f: f.write(file_data_b)
            except: pass
        else:
            print(f"Other Form. Data:\n{str(request_forms[form])}\n")

@app.get("/")
async def ping(request: Request):
    return Response(status_code=200)

@app.post("/callback/post/json/noauth")
async def post_json_noauth(request: Request):
    log_base_method_call(request)
    try: await handle_json_payload(request)
    except: return Response(status_code=400)
    return Response(status_code=200)

@app.post("/callback/post/csv/noauth")
async def post_csv_noauth(request: Request):
    log_base_method_call(request)
    try: await handle_csv_payload(request)
    except: return Response(status_code=400)
    return Response(status_code=200)

@app.post("/callback/post/json/oauth")
async def post_json_jwt(request: Request):
    log_base_method_call(request)
    try: await handle_json_payload(request)
    except: return Response(status_code=400)
    try: await handle_jwt_token(request)
    except: return Response(status_code=403)
    return Response(status_code=200)

@app.post("/callback/post/csv/oauth")
async def post_csv_jwt(request: Request):
    log_base_method_call(request)
    try: await handle_csv_payload(request)
    except: return Response(status_code=400)
    try: await handle_jwt_token(request)
    except: return Response(status_code=403)
    return Response(status_code=200)

@app.post("/callback/post/failure/noauth")
async def post_failure_noauth(request: Request):
    log_base_method_call(request)
    print("Failure callack received.\n")
    return Response(status_code=500)
