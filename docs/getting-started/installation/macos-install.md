#  macOS Install

## Requirements

The kaos command-line utility is used for all interactions. It is rather lightweight but **requires** the following \(and on your `PATH`\) based on the assumed persona - **Data Scientist** vs. **Superhero**. Check [kaos personas](../../usage/high-level-usage/#kaos-personas) for more information

{% tabs %}
{% tab title="Data Scientist" %}
* [**jq**](https://stedolan.github.io/jq/download/) ****for processing JSON

  ```bash
  brew install jq
  ```

* \*\*\*\*[**coreutils**](https://www.gnu.org/software/coreutils/) ****for additional core utilities

  ```bash
  brew install coreutils
  ```

* \*\*\*\*[**graphviz**](https://www.graphviz.org/download/) ****for visualization of data provenance

  ```bash
  brew install graphviz
  ```

* \*\*\*\*[**python 3.7**](https://www.python.org/downloads/) ****for running all kaos commands

  ```bash
  brew install python3
  ```
{% endtab %}

{% tab title="Superhero" %}
* [**jq**](https://stedolan.github.io/jq/download/) ****for processing JSON

  ```bash
  brew install jq
  ```

* \*\*\*\*[**coreutils**](https://www.gnu.org/software/coreutils/) ****for additional core utilities

  ```bash
  brew install coreutils
  ```

* \*\*\*\*[**graphviz**](https://www.graphviz.org/download/) ****for visualization of data provenance

  ```bash
  brew install graphviz
  ```

* \*\*\*\*[**docker**](https://docs.docker.com/install/linux/docker-ce/ubuntu/) for dynamic linking of docker registry \(function of `kaos build`\)

  ```bash
  brew install docker
  ```

* \*\*\*\*[**kubectl**](https://kubernetes.io/docs/tasks/tools/install-kubectl/) for interacting with the kaos cluster

  ```bash
  export version=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)
  curl -LO "https://storage.googleapis.com/kubernetes-release/release/${version}/bin/darwin/amd64/kubectl"
  chmod +x kubectl
  mv kubectl /usr/local/bin/
  ```

* [**Terraform**](https://learn.hashicorp.com/terraform/getting-started/install.html) ****for building entire infrastructure as IaC \(see [Deploying Infrastructure](../deploying-infrastructure/)\)

  ```bash
  brew install terraform
  ```

* [**python 3.7**](https://www.python.org/downloads/) ****for running all kaos commands

  ```bash
  brew install python3
  ```

* [**awscli**](https://aws.amazon.com/cli/) for deploying infrastructure on AWS **\[OPTIONAL\]**

  ```bash
  pip3 install awscli
  ```

* \*\*\*\*[**aws authenticator**](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html) ****for deploying Kubernetes \(EKS\) in AWS **\[OPTIONAL\]**

  ```bash
  brew install aws-iam-authenticator
  ```

* \*\*\*\*[**gcloud**](https://cloud.google.com/sdk/docs/quickstart-macos) ****for deploying infrastructure on GCP **\[OPTIONAL\]**

  ```bash
  export CLOUD_SDK_VERSION=267.0.0
  curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-darwin-x86_64.tar.gz
  tar zxvf google-cloud-sdk-${CLOUD_SDK_VERSION}-darwin-x86_64.tar.gz google-cloud-sdk
  rm google-cloud-sdk-${CLOUD_SDK_VERSION}-darwin-x86_64.tar.gz
  export PATH=./google-cloud-sdk/bin:$PATH
  gcloud --version
  ```
{% endtab %}
{% endtabs %}

## Installation

kaos supports **two** installation methods based on the desired simplicity and environment.

| Methods | Description |
| :--- | :--- |
| Automatic \[**Recommended**\] | Isolated dependencies **with** a virtual environment \(requires [**pipenv**](https://docs.pipenv.org/en/latest/install/#installing-pipenv)\) |
| Manual \[**Advanced**\] | Manual installation **without** a virtual environment  |

{% hint style="info" %}
Note that the following installation steps assume the kaos repository is accessed by **HTTPS**
{% endhint %}

### Automatic Installation \[Recommended\]

The **recommended** installation of kaos is done automatically within a virtual environment using [**pipenv**](https://docs.pipenv.org/en/latest/install/#installing-pipenv). The following steps will ensure a successful **isolated** installation of kaos.

```bash
git clone https://github.com/KI-labs/kaos.git
cd ./kaos
pipenv install && pipenv shell
```

{% hint style="success" %}
An isolated installation of kaos within a **virtual environment** is the **ideal** installation
{% endhint %}

### Manual Installation \[Advanced\]

The following steps will ensure a successful installation of kaos.

```bash
git clone https://github.com/KI-labs/kaos.git
cd ./kaos
cd model && python3 setup.py install
cd ../cli && python3 setup.py install
```

### Successful Installation

Running `kaos` will greet the user with the following response.

![](../../.gitbook/assets/image%20%2850%29.png)

Refer to [**Quick Start**](../quick-start.md#2-create-a-workspace) for hands-on experience with training and serving a model within kaos.

