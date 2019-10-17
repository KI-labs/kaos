# Microsoft Azure (AZ)

**NOTE THAT AZURE IS UNSUPPORTED IN THE LATEST KAOS RELEASE**

<!---
### Getting Started

There are quite a few number of variables that are required to connect Terraform and Azure. For security purposes,
it is ideal to have them read as environment variables rather then push and distribute in Git. The following variables
need to be sourced as environment variables.

```
$ export TF_VAR_CLIENT_ID=xxx-xxx-xxxx-xxxx-xxxx
$ export TF_VAR_CLIENT_SECRET=xxx-xxx-xxxx-xxxx-xxxx
$ export TF_VAR_SERVICE_PRINCIPAL_ID=xxx-xxx-xxxx-xxxx-xxxx
$ export TF_VAR_SERVICE_PRINCIPAL_SECRET=xxx-xxx-xxxx-xxxx-xxxx
$ export TF_VAR_SUBSCRIPTION_ID=xxx-xxx-xxxx-xxxx-xxxx
$ export TF_VAR_TENANT_ID=xxx-xxx-xxxx-xxxx-xxxx
$ export ARM_ACCESS_KEY=xxx-xxx-xxxx-xxxx-xxxx
$ export TF_VAR_registry_email=<your-azure@email>
$ export TF_VAR_admin_username=<your-admin-username>
```

### Tests with InSpec

InSpec is a tool written in Ruby that tests the different aspects of the infrastructure on different cloud
platforms. For that, one needs to simply install the inspec gem. The Gemfile is already present that can be used to
install it.

Now, to test the environment for Terraform, one needs to export an environment variable to avoid code redundancy.

```
$ export ENVIRONMENT=dev
$ inspec exec integration/ -t azure://
```

The supported environments are *dev*, *stage* and *prod*.

### Credentials

To provide the Azure specific credentials, one can either export them as environment variables or store them in a file.
The following Environment variables are required

```
$ export SUBSCRIPTION_ID=xxxx-xxxxx-xxxx-xxxxx-xx-xxxxx
$ export CLIENT_ID=xxxx-xxxxx-xxxx-xxxxx-xx-xxxxx
$ export CLIENT_SECRET=xxxx-xxxxx-xxxx-xxxxx-xx-xxxxx
$ export TENANT_ID=xxxx-xxxxx-xxxx-xxxxx-xx-xxxxx
```

To store them as a file, create a hidden file in the home folder in the following format

```
$ mkdir ~/.azure/credentials

[xxxx-xxxxx-YOUR_SUBSCRIPTION_ID-xxxxx-xx-xxxxx]
client_id=xxxx-xxxxx-xxxx-xxxxx-xx-xxxxx
client_secret=xxxx-xxxxx-xxxx-xxxxx-xx-xxxxx
tenant_id=xxxx-xxxxx-xxxx-xxxxx-xx-xxxxx

```

### Kubectl
To avoid cluttering the main kubeconfig file (i.e. ``~/.kube/config ``) with several cluster definition 
we save an environment specific kubeconfig in each environment. To be able to interact with your deployed 
kubernetes cluster via kubectl you need to have the following environment variable set:
```
export KUBECONFIG=$(pwd)/envs/<your-desireder-env>/kubeconfig_kaos-2-<your-desireder-env>

``` 
-->
