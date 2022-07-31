#!/usr/bin/env bash

if [ $# -ge 1 ]; then
    export KUBECONFIG=$1
fi

NS=mosip-token-seeder

kubectl -n $NS delete --ignore-not-found=true secret tokenseeder-partner-creds
kubectl -n $NS delete --ignore-not-found=true secret tokenseeder-partner-certs-secret
helm -n $NS delete mosip-token-seeder