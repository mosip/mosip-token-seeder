# MOSIP Token Seeder

## Overview

Refer [documentation](https://docs.mosip.io/openg2p/mosip-token-seeder).

## Running for Development

### Pre-requisites
- Install the following packages (or equivalent ones for your system).
    ```sh
    sudo apt install libsqlcipher-dev libsqlite3-dev
    ```
- Initialize virtualenv:
    ```sh
    virtualenv venv_token_seeder
    ```
- Edit the `activate` file of the virtualenv (`venv_token_seeder/bin/activate`), and add the following lines in the end of the file.
    ```sh
    export TOKENSEEDER_GUNICORN__WORKERS=3
    export TOKENSEEDER_GUNICORN__MAX_REQUESTS=10000
    export TOKENSEEDER_GUNICORN__TIMEOUT=5
    export TOKENSEEDER_GUNICORN__KEEP_ALIVE=5
    export TOKENSEEDER_DB__LOCATION="sqlite:///auth_token_seeder.dbsqlite"
    export TOKENSEEDER_DB__GENERATE_DB_ALWAYS="false"
    export TOKENSEEDER_MOSIP_AUTH__PARTNER_APIKEY=
    export TOKENSEEDER_MOSIP_AUTH__PARTNER_MISP_LK=
    export TOKENSEEDER_MOSIP_AUTH__PARTNER_ID=
    export TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_DOMAIN_URI=
    export TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_URL=
    export TOKENSEEDER_CRYPTO_ENCRYPT__ENCRYPT_CERT_PATH=
    export TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PATH=
    export TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PASSWORD=

    alias run_token_seeder_dev='TOKENSEEDER_DB__PASSWORD=$(python3 -m mosip_token_seeder.repository dbinit) gunicorn -n "gunicorn" --worker-class uvicorn.workers.UvicornWorker --workers ${TOKENSEEDER_GUNICORN__WORKERS} --bind 0.0.0.0:8080 --max-requests ${TOKENSEEDER_GUNICORN__MAX_REQUESTS} --timeout ${TOKENSEEDER_GUNICORN__TIMEOUT} --keep-alive ${TOKENSEEDER_GUNICORN__KEEP_ALIVE} --access-logfile "-" --error-logfile "-" app:app'
    ```
- Create a new folder `certs`, and place the client certificates, etc there. 
- Configure the above environment variables in the activate script with the appropriate client details and certs.
- Install the python requirements:
    ```sh
    source venv_token_seeder/bin/activate
    pip3 install -r mosip_token_seeder/requirements.txt
    deactivate
    ```

### Running
-   ```sh
    source venv_token_seeder/bin/activate
    run_token_seeder_dev
    ```
    Access localhost:8080 on browser. Access localhost:8080/docs for apidocs.
- For running only the authenticator for single authentication:
  - Configure `mosip_auth`, `mosip_auth_server` and `crypto_` sections in `authenticator/authenticator-config.toml`. And place the certificate and keys appropriately.
  - Then run (sample json given in samples folder):
      ```sh
      python3 -m mosip_token_seeder.authenticator demoauth <json>
      ```


## Running the Docker
```sh
docker run -it --rm \
    --name token-seeder \
    -p 8080:8080 \
    -v <local-certs-path>:/seeder/certs \
    -e TOKENSEEDER_MOSIP_AUTH__PARTNER_APIKEY= \
    -e TOKENSEEDER_MOSIP_AUTH__PARTNER_MISP_LK= \
    -e TOKENSEEDER_MOSIP_AUTH__PARTNER_ID= \
    -e TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_DOMAIN_URI= \
    -e TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_URL= \
    -e TOKENSEEDER_CRYPTO_ENCRYPT__ENCRYPT_CERT_PATH=/seeder/certs/<ida.partner.cert> \
    -e TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PATH=/seeder/certs/<client.p12> \
    -e TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PASSWORD= \
    mosipdev/mosip-token-seeder:develop
```

## Installing on k8s cluster using the helm
- Install `kubectl` and `helm` utilities. Then run:
    ```sh
    cd helm
    ./install.sh [cluster-kubeconfig-file]
    ```
