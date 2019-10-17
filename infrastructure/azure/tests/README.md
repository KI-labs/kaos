# Azure tests with InSpec

InSpec is a tool written in Ruby that tests the different aspects of the infrastructure on different cloud
platforms. For that, one needs to simply install the inspec gem. The Gemfile is already present that can be used to
install it.

Now, to test the environment for Terraform, one needs to export an environment variable to avoid code redundancy.

```
$ export ENVIRONMENT=dev
$ inspec exec terraform/ -t azure://
```

The supported environments are *dev*, *stage* and *prod*.

## Credentials

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
