# MOSIP Token Seeder

![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)

## Overview

The `mosip-token-seeder` is a critical component designed to facilitate the seeding of authentication tokens into the MOSIP ecosystem. It acts as a bridge, allowing external systems to securely inject authentication data (like VID, demographics, and biometrics via ODK) which are then processed and validated against the MOSIP ID Authentication APIs. This service creates a secure and efficient mechanism for pre-populating authentication contexts, essential for various offline and online verification scenarios.

## Features

-   **JSON Token Seeding**: Supports seeding authentication tokens via JSON payloads.
-   **CSV Batch Seeding**: Allows bulk upload of token requests using CSV files.
-   **ODK Integration**: Specialized support for Open Data Kit (ODK) based data collection and token generation.
-   **MOSIP Auth Integration**: Seamlessly connects with MOSIP IDA (ID Authentication) services to perform demographic authentication.
-   **Secure Storage**: Utilizes SQLCipher for encrypted storage of sensitive token data.
-   **Configurable Policies**: Flexible configuration for authentication partner IDs, policies, and logging.
-   **Automated Cleanup**: Scheduled cleanup jobs to remove expired token entries.
-   **FastAPI Framework**: Built on FastAPI with async support for high performance.

## Services

The repository comprises the following key services:

1.  **Auth Token API (`authtokenapi`)**
    -   **Purpose**: Exposes REST endpoints to receive token seeding requests (JSON, CSV, ODK).
    -   **Function**: Validates incoming data, initiates the seeding process, and provides request status.
    -   **Endpoints**:
        -   `POST /authtoken/json` - Submit token request via JSON payload
        -   `POST /authtoken/csv` - Submit token request via CSV file upload
        -   `POST /authtoken/odk` - Submit token request via ODK format
        -   `GET /authtoken/status/{id}` - Get status of a token request
        -   `GET /authtoken/file/{id}` - Download generated token file
        -   `GET /authtoken/authfields` - Get list of available authentication fields
        -   `GET /ping` - Health check endpoint

2.  **Authenticator (`authenticator`)**
    -   **Purpose**: Handles the core logic of communicating with MOSIP IDA.
    -   **Function**: Encrypts and signs identity blocks, constructs auth requests, and manages the handshake with the MOSIP Auth server.

3.  **Repository (`repository`)**
    -   **Purpose**: Data persistence layer.
    -   **Function**: Manages connections to the SQLCipher database, handling the storage and retrieval of token request data and status.

4.  **Token Seeder (`tokenseeder`)**
    -   **Purpose**: Core token generation and processing logic.
    -   **Function**: Processes queued requests, generates tokens, and manages cleanup operations.

## Local Setup

There are two primary ways to deploy the `mosip-token-seeder` locally:

1.  **Local Python Environment**: Running directly on the host machine using a virtual environment.
    -   See sections [Prerequisites](#prerequisites), [Database Setup](#database-setup), and [Configurations](#configurations).
    -   After configuration, run the application using the commands in the [Configurations](#configurations) section.
2.  **Docker**: Running as a containerized application.
    -   See [Local Setup using Docker Image](#local-setup-using-docker-image) for running an existing image.
    -   See [Local Setup by Building Docker Image](#local-setup-by-building-docker-image) for building and running locally.

## Prerequisites

Before setting up, ensure you have the following prerequisites services and modules:

-   **Python**: Version 3.8 or higher (Python 3.8.13 is used in the Docker image).
-   **System Packages**: Install `libsqlcipher-dev` and `libsqlite3-dev` (or equivalent for your OS).
    ```sh
    sudo apt install libsqlcipher-dev libsqlite3-dev
    ```
-   **Virtual Environment**:
    -   Initialize: `virtualenv venv_token_seeder`
    -   Activate: `source venv_token_seeder/bin/activate` (Linux/Mac) or `venv_token_seeder\Scripts\activate` (Windows)
-   **Python Dependencies**: Install required packages:
    ```sh
    pip install -r mosip_token_seeder/requirements.txt
    ```
-   **MOSIP Connectivity**: Access to a running MOSIP instance (specifically the IDA Auth service).
-   **Client Certificates**: A folder `certs` containing the client certificates:
    -   `ida.partner.cert` - Partner certificate for encryption
    -   `keystore.p12` (or `client.p12`) - P12 keystore file for signing

## Database Setup

The database functionality uses SQLite with SQLCipher encryption for secure storage of token data.

**Steps:**
1.  Navigate to the project root.
2.  If running for the first time or forcing regeneration, set the environment variable:
    ```bash
    export TOKENSEEDER_DB__GENERATE_DB_ALWAYS="true"
    ```
3.  Initialize the database schema:
    ```bash
    python3 -m mosip_token_seeder.repository dbinit
    ```
    This command:
    -   Creates the encrypted SQLite database file `auth_token_seeder.dbsqlite`
    -   Generates a random password (if `TOKENSEEDER_DB__GENERATE_PASSWORD_ALWAYS="true"`)
    -   Returns the database password (if `TOKENSEEDER_DB__PRINT_PASSWORD_ON_STARTUP="true"`)
4.  The database password is automatically generated and can be retrieved from the startup logs if `TOKENSEEDER_DB__PRINT_PASSWORD_ON_STARTUP="true"` is set.

## Configurations

The application relies on environment variables for configuration. Configuration is managed through Dynaconf, which supports TOML files and environment variables with the `TOKENSEEDER` prefix.

### Environment Variables

Add the following exports to your virtualenv `activate` script (`venv_token_seeder/bin/activate` on Linux/Mac or `venv_token_seeder\Scripts\activate` on Windows) or set them in your environment:

**Server Configuration:**
```sh
export TOKENSEEDER_GUNICORN__WORKERS=3
export TOKENSEEDER_GUNICORN__MAX_REQUESTS=10000
export TOKENSEEDER_GUNICORN__TIMEOUT=5
export TOKENSEEDER_GUNICORN__KEEP_ALIVE=5
```

**Database Configuration:**
```sh
export TOKENSEEDER_DB__LOCATION="sqlite:///auth_token_seeder.dbsqlite"
export TOKENSEEDER_DB__GENERATE_DB_ALWAYS="false"
export TOKENSEEDER_DB__GENERATE_PASSWORD_ALWAYS="true"
export TOKENSEEDER_DB__PRINT_PASSWORD_ON_STARTUP="true"
export TOKENSEEDER_DB__PASSWORD=""  # Auto-generated if not set
```

**MOSIP Authentication Configuration:**
```sh
export TOKENSEEDER_MOSIP_AUTH__PARTNER_APIKEY="your-api-key"
export TOKENSEEDER_MOSIP_AUTH__PARTNER_MISP_LK="your-misp-lk"
export TOKENSEEDER_MOSIP_AUTH__PARTNER_ID="your-partner-id"
export TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_DOMAIN_URI="https://your-mosip-instance.com"
export TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_URL="https://your-mosip-instance.com/v1/authmanager/authenticate"
```

**Cryptography Configuration:**
```sh
export TOKENSEEDER_CRYPTO_ENCRYPT__ENCRYPT_CERT_PATH="/path/to/certs/ida.partner.cert"
export TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PATH="/path/to/certs/keystore.p12"
export TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PASSWORD="your-p12-password"
```

**Optional Configuration:**
```sh
export TOKENSEEDER_ROOT__SYNC_OPERATION_MODE="false"  # Enable synchronous token generation
export TOKENSEEDER_AUTHTOKEN__MANDATORY_VALIDATION_AUTH_FIELDS="name,gender,dob,fullAddress"
export TOKENSEEDER_CLEANUP__ENABLED="true"
export TOKENSEEDER_CLEANUP__CLEANUP_INTERVAL_SECONDS="21600"  # 6 hours
export TOKENSEEDER_CLEANUP__CLEANUP_EXPIRY_SECONDS="21600"  # 6 hours
```

### Running the Application

**Convenience Alias (Linux/Mac):**
You can define an alias to run the application easily:
```sh
alias run_token_seeder_dev='TOKENSEEDER_DB__PASSWORD=$(python3 -m mosip_token_seeder.repository dbinit) gunicorn -n "gunicorn" --worker-class uvicorn.workers.UvicornWorker --workers ${TOKENSEEDER_GUNICORN__WORKERS} --bind 0.0.0.0:8080 --max-requests ${TOKENSEEDER_GUNICORN__MAX_REQUESTS} --timeout ${TOKENSEEDER_GUNICORN__TIMEOUT} --keep-alive ${TOKENSEEDER_GUNICORN__KEEP_ALIVE} --access-logfile "-" --error-logfile "-" app:app'
```

**Direct Command:**
```sh
TOKENSEEDER_DB__PASSWORD=$(python3 -m mosip_token_seeder.repository dbinit) gunicorn --worker-class uvicorn.workers.UvicornWorker --workers 3 --bind 0.0.0.0:8080 app:app
```

## Local Setup using Docker Image

To run the module locally using an existing docker image:

```sh
docker run -it --rm \
    --name token-seeder \
    -p 8080:8080 \
    -v <local-certs-path>:/seeder/certs \
    -e TOKENSEEDER_MOSIP_AUTH__PARTNER_APIKEY="your-api-key" \
    -e TOKENSEEDER_MOSIP_AUTH__PARTNER_MISP_LK="your-misp-lk" \
    -e TOKENSEEDER_MOSIP_AUTH__PARTNER_ID="your-partner-id" \
    -e TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_DOMAIN_URI="https://your-mosip-instance.com" \
    -e TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_URL="https://your-mosip-instance.com/v1/authmanager/authenticate" \
    -e TOKENSEEDER_CRYPTO_ENCRYPT__ENCRYPT_CERT_PATH=/seeder/certs/ida.partner.cert \
    -e TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PATH=/seeder/certs/keystore.p12 \
    -e TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PASSWORD="your-p12-password" \
    mosipdev/mosip-token-seeder:develop
```

**Note:** Replace `<local-certs-path>` with the absolute path to your local certificates directory, and fill in all the required environment variable values.

## Local Setup by Building Docker Image

To build and run the docker image locally:

1.  **Build the Image**:
    ```bash
    docker build -t mosip-token-seeder:local .
    ```
2.  **Run the Container**:
    Use the same `docker run` command as above, but replace the image name `mosipdev/mosip-token-seeder:develop` with `mosip-token-seeder:local`.

## Deployment

### Kubernetes/Helm Deployment

For deploying to a Kubernetes cluster using Helm:

1.  Navigate to the `helm` directory:
    ```sh
    cd helm
    ```
2.  Configure the following sections in `values.yaml`:
    -   `seeder.mandatoryValidationFields` - Required authentication fields (default: `"name,gender,dob,fullAddress"`)
    -   `seeder.cleanup` - Cleanup job configuration (enabled, interval, expiry)
    -   `seeder.mosipAuth` - MOSIP authentication server URLs
    -   `seeder.crypto` - Certificate paths
    -   `seeder.partnerCredsSecret` - Secret name for partner credentials
    -   `seeder.certsSecret` - Secret name for certificates
3.  Create required Kubernetes secrets:
    ```sh
    kubectl create secret generic tokenseeder-partner-creds \
        --from-literal=partner-api-key=<api-key> \
        --from-literal=partner-misp-lk=<misp-lk> \
        --from-literal=partner-id=<partner-id> \
        --from-literal=sign-p12-password=<p12-password>
    
    kubectl create secret generic tokenseeder-partner-certs-secret \
        --from-file=ida.partner.cert=<path-to-cert> \
        --from-file=keystore.p12=<path-to-p12>
    ```
4.  Run the install script:
    ```sh
    ./install.sh [cluster-kubeconfig-file]
    ```
5.  Alternatively, use Helm directly:
    ```sh
    helm install mosip-token-seeder . -f values.yaml
    ```

## Upgrade

-   **Kubernetes/Helm**: 
    -   Update the `values.yaml` with new configuration
    -   Pull the latest Helm chart
    -   Run upgrade: `helm upgrade mosip-token-seeder . -f values.yaml`
    -   Or use the install script: `./install.sh [cluster-kubeconfig-file]`
-   **Docker**: 
    -   Pull the latest image tag: `docker pull mosipdev/mosip-token-seeder:develop`
    -   Stop and remove the existing container
    -   Run the new container with the same configuration
-   **Local**: 
    -   Pull latest git changes: `git pull`
    -   Reinstall requirements: `pip3 install -r mosip_token_seeder/requirements.txt --upgrade`
    -   Restart the service

## API Usage Examples

### JSON Token Request

```bash
curl -X POST "http://localhost:8080/authtoken/json" \
  -H "Content-Type: application/json" \
  -d @samples/auth_token_request.json
```

### Check Request Status

```bash
curl -X GET "http://localhost:8080/authtoken/status/{request_identifier}"
```

### Download Generated File

```bash
curl -X GET "http://localhost:8080/authtoken/file/{request_identifier}" \
  -o output.csv
```

### Get Available Auth Fields

```bash
curl -X GET "http://localhost:8080/authtoken/authfields"
```

### Health Check

```bash
curl -X GET "http://localhost:8080/ping"
```

## Documentation

### API Documentation
API endpoints, base URL (repo name), and mock server details are available via Stoplight and Swagger documentation:
-   [API Documentation Link](https://mosip.stoplight.io/docs/mosip-token-seeder)

### Product Documentation
To know more about `mosip-token-seeder` in the perspective of functional and use cases you can refer to our main document:
-   [MOSIP Documentation](https://docs.mosip.io/openg2p/mosip-token-seeder)

## Contribution & Community

We welcome contributions from everyone!

[Check here](https://docs.mosip.io/1.2.0/community/code-contributions) to learn how you can contribute code to this application.

If you have any questions or run into issues while trying out the application, feel free to post them in the [MOSIP Community](https://community.mosip.io/) — we’ll be happy to help you out.

-   [GitHub Issues](https://github.com/mosip/mosip-token-seeder/issues)
