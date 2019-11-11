# Cloud

{% hint style="warning" %}
Cluster makeup \(instance type and size\) **must** be defined before running `kaos build`
{% endhint %}

Check [AWS](https://aws.amazon.com/ec2/instance-types/) or [GCP](https://cloud.google.com/compute/docs/machine-types) for more details on the available instance types in your respective compute region.

The state of the infrastructure deployment is handled within the terraform [backend](https://www.terraform.io/docs/backends/index.html). kaos allows the user to use either a local or remote backend with the available `-l` or `--local_backend` option. Deploying a local backend should only be considered for testing purposes since it resides **locally**.

## Amazon Web Services \(AWS\)

The cluster type and size can be specified through `ENV` based on the following naming convention:

```bash
# (optional) cluster "makeup"
export TF_VAR_worker_groups_type=cpu_gpu|cpu_only (default: cpu_only)

# CPU autoscaling group
export TF_VAR_cpu_min_node_count=<int> (default: 1)
export TF_VAR_cpu_max_node_count=<int> (default: 5)
export TF_VAR_cpu_desired_node_count=<int> (default: 2)
export TF_VAR_cpu_instance_type_aws=<str> (default: "m5.large")
export TF_VAR_cpu_autoscaling_enabled=<bool> (default: true)

# (optional) GPU autoscaling group
export TF_VAR_gpu_min_node_count=<int> (default: 0)
export TF_VAR_gpu_max_node_count=<int> (default: 1)
export TF_VAR_gpu_desired_node_count=<int> (default: 1)
export TF_VAR_gpu_instance_type_aws=<str> (default: "p2.xlarge")
export TF_VAR_gpu_autoscaling_enabled=<bool> (default: true)

# (optional) backend API memory/cpu configuration
export TF_VAR_api_memory_request=<str> (default: "1Gi")
export TF_VAR_api_memory_limit=<str> (default: "2Gi")
export TF_VAR_api_cpu_request=<float> (default: 0.5)
export TF_VAR_api_cpu_limit=<float> (default: 1.5)
```

A successful build of kaos within AWS requires [programmatic access](https://docs.aws.amazon.com/IAM/latest/UserGuide/console.html) and running an [EKS authenticator](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html). The following `ENV` need to be exported to ensure correct authentication.

```bash
# mandatory AWS access information
export AWS_ACCESS_KEY_ID=#########
export AWS_SECRET_ACCESS_KEY=#########
export AWS_DEFAULT_REGION=#########
```

kaos can be built and destroyed within **AWS** with the following commands.

```bash
kaos build -c AWS -v
kaos destroy -c AWS -v
```

{% hint style="success" %}
It can take upwards of **15 minutes** to successfully deploy a kaos cluster in **AWS**
{% endhint %}

## Google Cloud Platform \(GCP\)

The cluster type and size can be specified through `ENV` based on the following naming convention

```bash
# (optional) cluster "makeup"
export TF_VAR_worker_groups_type=cpu_gpu|cpu_only (default: cpu_only)

# CPU node pool
export TF_VAR_cpu_min_node_count=<int> (default: 1)
export TF_VAR_cpu_max_node_count=<int> (default: 5)
export TF_VAR_cpu_desired_node_count=<int> (default: 2)
export TF_VAR_cpu_instance_type_gcp=<str> (default: "n1-standard-2")

# (optional) GPU autoscaling group
export TF_VAR_gpu_min_node_count=<int> (default: 0)
export TF_VAR_gpu_max_node_count=<int> (default: 1)
export TF_VAR_gpu_desired_node_count=<int> (default: 1)
export TF_VAR_gpu_instance_type_gcp=<str> (default: "n1-standard-4")
export TF_VAR_gpu_accelerator_count=<int> (default: 1)
export TF_VAR_gpu_accelerator_type=<str> (default: "nvidia-tesla-p100")

# (optional) backend API memory/cpu configuration
export TF_VAR_api_memory_request=<str> (default: "1Gi")
export TF_VAR_api_memory_limit=<str> (default: "2Gi")
export TF_VAR_api_cpu_request=<float> (default: 0.5)
export TF_VAR_api_cpu_limit=<float> (default: 1.5)
```

### Cluster Location

The following variables are available to control cluster and resource location.

```bash
export TF_VAR_project_location=<str> # (for example: us-west1-a)
export TF_VAR_project_region=<str> # (for example: us)
```

* `project_location` specifies the location of cluster and network
* `project_region` specifies the location of storage and docker repository 

### Build

A successful build of kaos within GCP requires a \(service\) account with the following roles:

* Compute Network Admin
* Kubernetes Engine Admin
* Kubernetes Engine Cluster Admin
* Kubernetes Engine Developer
* Storage Admin
* Storage Object Admin
* Role Viewer
* Security Viewer
* Create Service ACcounts
* Service Account User

The following `ENV` need to be exported based on [GCP authentication instructions](https://cloud.google.com/docs/authentication/getting-started#auth-cloud-implicit-python).

```bash
# mandatory GCP access information
export GOOGLE_APPLICATION_CREDENTIALS="</path/to/credential.json>"
```

kaos can be built and destroyed within **GCP** with the following commands.

```bash
kaos build -c GCP -v
kaos destroy -c GCP -v
```

{% hint style="success" %}
It can take upwards of **15 minutes** to successfully deploy a kaos cluster in **GCP**
{% endhint %}

## Microsoft Azure \(AZ\)

{% hint style="danger" %}
Note that Azure is not fully implemented for the current release
{% endhint %}

