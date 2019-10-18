#!/bin/bash
set -e

# define arguments
for i in "$@"
do
case ${i} in
    -a=*|--auth=*)
    CREDENTIALS_PATH="${i#*=}"
    shift # past argument=value
    ;;
    -r=*|--region=*)
    REGION="${i#*=}"
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

# get the region defined in the current configuration
echo "==========================="
echo "| Configure GCP region... |"
echo "==========================="
if [[ -z "$REGION" ]]
    then
        REGION="eu"
fi
echo "+${REGION} being used"

echo "========================================"
echo "| Logging in to GCP docker registry... |"
echo "========================================"
cat ${CREDENTIALS_PATH} | docker login -u _json_key --password-stdin https://"${REGION}.gcr.io"
