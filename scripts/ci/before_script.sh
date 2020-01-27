#!/usr/bin/env bash
set -e

sudo rm -rf /var/lib/apt/lists/*
sudo apt-get update
sudo apt-get install coreutils unzip graphviz socat

echo "install cli requirements"
pip3 install ./model

echo "install terraform"
wget https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip
unzip terraform_${TF_VERSION}_linux_amd64.zip
sudo mv terraform /usr/local/bin/

echo "terraform version"
terraform --version

echo "install minikube and kubectl"
curl -Lo minikube https://storage.googleapis.com/minikube/releases/${M6E_VER}/minikube-linux-amd64
curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/v${K8S_VER}/bin/linux/amd64/kubectl
sudo chmod +x kubectl
sudo chmod +x minikube
sudo mv kubectl /usr/local/bin/
sudo mv minikube /usr/local/bin/

echo "starting minikube"
sudo minikube start --vm-driver=none --kubernetes-version=v${K8S_VER} --cpus=2 --memory=4096 --bootstrapper=localkube
minikube update-context

JSONPATH='{range .items[*]}{@.metadata.name}:{range @.status.conditions[*]}{@.type}={@.status};{end}{end}'; until kubectl get nodes -o jsonpath="$JSONPATH" 2>&1 | grep -q "Ready=True"; do sleep 1; done
