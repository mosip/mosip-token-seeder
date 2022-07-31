#!/usr/bin/env bash
if [ $# -ge 1 ]; then
    export KUBECONFIG=$1
fi

get_set_env(){
    if [ -z "${!1}" ]; then
        if [ -z "$2" ]; then prompt="Give $1 :"; else prompt="$2"; fi
        if [ -z "$3" ]; then default=""; else default="$3" ; fi
        read -p "${prompt} (default: ${default}) " "var"
        if [ -n "$var" ]; then export $1="$var"; else export $1="$default"; fi
        unset var
    else
        export $1="${!1}"
    fi
}

NS=mosip-token-seeder

get_set_env "TOKENSEEDER_MOSIP_AUTH__PARTNER_ID" "Give Parther Id :"
get_set_env "TOKENSEEDER_MOSIP_AUTH__PARTNER_APIKEY" "Give Parther API Key :"
get_set_env "TOKENSEEDER_MOSIP_AUTH__PARTNER_MISP_LK" "Give Parther MISP License Key :"
get_set_env "TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_URL" "Give MOSIP Auth Server Url :" "https://api.mosip.net/idauthentication/v1/auth"
get_set_env "TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_DOMAIN_URI" "Give MOSIP Auth Domain :" "https://api.mosip.net"
get_set_env "TOKENSEEDER_CRYPTO_ENCRYPT__ENCRYPT_CERT_PATH" "Give Path to IDA Partner Cert:" "certs/ida.partner.cert"
get_set_env "TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PATH" "Give Path to Partner P12 file :" "certs/keystore.p12"
get_set_env "TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PASSWORD" "Give Password for abgove P12 file :"
get_set_env "should_ingress_istio" "Should Install istio or ingress :" "ingress"

if [ "$should_ingress_istio" = "ingress" ]; then
    ingress_enabled="true"; istio_enabled="false"
    get_set_env "ingress_hostname" "Ingress Hostname :" "api.sandbox.net"
elif [ "$should_ingress_istio" = "istio" ]; then
    ingress_enabled="false"; istio_enabled="true"
    get_set_env "istio_gateway" "Please create an istio gateway seperately. Pass the name of the gateway here :"
else
    ingress_enabled="false"; istio_enabled="false"
fi

echo Updating Helm Dependencies
helm dependency update

echo Create $NS namespace
kubectl create ns $NS

if [ "$istio_enabled" = "true" ]; then
    echo Istio Injection Enabled
    kubectl label ns $NS istio-injection=enabled --overwrite
fi

kubectl -n $NS delete --ignore-not-found=true secret tokenseeder-partner-creds
kubectl -n $NS create secret generic tokenseeder-partner-creds \
    --from-literal=TOKENSEEDER_MOSIP_AUTH__PARTNER_ID=$TOKENSEEDER_MOSIP_AUTH__PARTNER_ID \
    --from-literal=TOKENSEEDER_MOSIP_AUTH__PARTNER_APIKEY=$TOKENSEEDER_MOSIP_AUTH__PARTNER_APIKEY \
    --from-literal=TOKENSEEDER_MOSIP_AUTH__PARTNER_MISP_LK=$TOKENSEEDER_MOSIP_AUTH__PARTNER_MISP_LK \
    --from-literal=TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PASSWORD=$TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PASSWORD

kubectl -n $NS delete --ignore-not-found=true secret tokenseeder-partner-certs-secret
kubectl -n $NS create secret generic tokenseeder-partner-certs-secret \
    --from-file=ida.partner.cert=$TOKENSEEDER_CRYPTO_ENCRYPT__ENCRYPT_CERT_PATH \
    --from-file=keystore.p12=$TOKENSEEDER_CRYPTO_SIGNATURE__SIGN_P12_FILE_PATH

helm -n $NS install mosip-token-seeder . \
    --set seeder.mosipAuth.idaAuthDomainUri="$TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_DOMAIN_URI" \
    --set seeder.mosipAuth.idaAuthUrl="$TOKENSEEDER_MOSIP_AUTH_SERVER__IDA_AUTH_URL" \
    --set ingress.enabled="$ingress_enabled" \
    --set ingress.hostname="$ingress_hostname" \
    --set istio.enabled="$istio_enabled" \
    --set istio.existingGateway="$istio_gateway"