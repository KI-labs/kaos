#!/usr/bin/env bash

set -e

check_deps () {
  test -f $(which kubectl) || error_exit "kubectl command not detected in path, please install it"
}

# define arguments
for i in "$@"
do
case ${i} in
    -t=*|--timeout=*)
    TIMEOUT="${i#*=}"
    shift # past argument=value
    ;;
    -i=*|--interval=*)
    INTERVAL="${i#*=}"
    shift # past argument=value
    ;;
    -k=*|--kubeconfig_path=*)
    KUBECONFIG_PATH="${i#*=}"
    shift # past argument=value
    ;;
    -n=*|--min_nodes=*)
    MIN_NODES="${i#*=}"
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

((END_TIME=${SECONDS}+${TIMEOUT}))
START_TIME=${SECONDS}
echo "The script ends at ${END_TIME}"
echo "Timeout is ${TIMEOUT}"
echo "Interval: ${INTERVAL}"

while ((${SECONDS} < ${END_TIME}))
do
  healthy_cnt=$(kubectl get nodes --kubeconfig=${KUBECONFIG_PATH} | egrep "Ready" | awk '{print $1}' | wc -w)

  if [[ ${healthy_cnt} -ge ${MIN_NODES} ]]
  then
    echo "Cluster is ready."
    exit 0
  fi

  elapsed=${SECONDS-START_TIME}
  echo "Still waiting for the Cluster to be in Ready state... Elapsed ${elapsed}sec"
  sleep ${INTERVAL}
done

echo "Timeout Exceed (${TIMEOUT}sec): Cluster is not running"
exit 1
