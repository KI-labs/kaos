#!/bin/bash

# Options:
#   -x: Echo commands
#   -e: Fail on errors
#   -o pipefail: Fail on errors in scripts this calls, give stacktrace
set -ex -o pipefail

###########################
# Terraform Installation
###########################
install_terraform () {
  echo " Installing Terraform "
  sudo apt-get update
  sudo apt-get install wget unzip apt-transport-https curl lsb-release gnupg jq python3-pip -y
  wget https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip
  unzip terraform_${TF_VERSION}_linux_amd64.zip
  sudo mv terraform /usr/local/bin
  terraform -v
}

###########################
# Kubectl Installation
###########################
install_kubectl () {
  echo "Installing Kubectl  "
  curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
  chmod +x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
}

###########################
#  Install AWS CLI
###########################
install_awscli () {
  echo "Installing AWS CLI"
  pip3 install awscli
  curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.13.7/2019-06-11/bin/linux/amd64/aws-iam-authenticator
  chmod +x ./aws-iam-authenticator
  mkdir -p $HOME/bin && cp ./aws-iam-authenticator $HOME/bin/aws-iam-authenticator && export PATH=$HOME/bin:$PATH
  echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc

  mkdir ~/.aws
  touch ~/.aws/credentials
  cat <<EOF > ~/.aws/credentials
[default]
aws_access_key_id = ${TF_VAR_aws_access_key_id}
aws_secret_access_key = ${TF_VAR_aws_secret_access_key}
EOF
}

###########################
#  Install AZ CLI
###########################
install_azcli () {
  echo "Installing AZ CLI"
  curl -sL https://packages.microsoft.com/keys/microsoft.asc | \
      gpg --dearmor | \
      sudo tee /etc/apt/trusted.gpg.d/microsoft.asc.gpg > /dev/null
  AZ_REPO=$(lsb_release -cs)
  echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
      sudo tee /etc/apt/sources.list.d/azure-cli.list
  sudo apt-get update
  sudo apt-get install azure-cli -y
}

install_terraform
install_kubectl
install_awscli
install_azcli

