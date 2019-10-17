#!/usr/bin/env bash

# define arguments
for i in "$@"
do
case ${i} in
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
echo "+${REGION} being used"

# login to ECR service
echo "==========================="
echo "| Login to ECR service... |"
echo "==========================="
$(aws ecr get-login --region ${REGION} --no-include-email)
echo "+success"
