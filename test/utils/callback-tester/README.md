## Build

- ```sh
    docker build . -t <image>
    ```
- ```sh
    docker push <image>
    ```

## Run Locally

- ```sh
    docker run -it --rm --name=callback \
        -e MAX_WORKERS=1 \
        -e JWKS_URI=<Jwks uri> \
        -p 8096:80 \
        -v $(pwd)/callback-test.py:/app/main.py \
        <image>
    ```
- If any changes to script required on the script, edit the script and rerun the above command.

## Run on K8S

- Change image in `callback-test.yaml`.
- Run
    ```sh
    kubectl -n <namespace> create cm tokenseeder-callback-tester-main --from-file=main.py=callback-test.py
    ```
    ```sh
    kubectl -n <namespace> apply -f callback-test.yaml
    ```
- If any changes to script required on the script, edit the configmap and restart pod.

