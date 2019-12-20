#!/bin/bash
set -e

export KAOS_HOME="$(pwd)"
echo "$KAOS_HOME"
K8S_PORT=30123

echo "installing cli"
cd cli
pip3 install -e .

echo "deploy kaos in integration testing dir"
cd ../testing/integration
ls -la .
kaos build deploy -c MINIKUBE -fvy
cat .kaos/config

echo "get main pods name"
AMBASSAROR_POD_NAME=`kubectl get pods | awk '{print $1}' | sed -n -e '/^ambassador/p'`
BACKEND_POD_NAME=`kubectl get pods | awk '{print $1}' | sed -n -e '/^backend/p'`

echo "set up port forwarding in order to access the ambassador endpoint"
kubectl port-forward ${AMBASSAROR_POD_NAME} ${K8S_PORT}:8080 &
kubectl get all

echo "installing tests"
pip3 install -e .
set +e
pytest --k8s-port=${K8S_PORT} --capture=no
status=$?

echo "output logs"
kubectl logs ${AMBASSAROR_POD_NAME}
kubectl logs ${BACKEND_POD_NAME}
exit ${status}