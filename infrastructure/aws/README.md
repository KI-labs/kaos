# Amazon Web Services (AWS)

### Requirements
- [aws_iam_authenticator][aws_authenticator]

### Environment Variables
The following env variables must be exported

```
export AWS_ACCESS_KEY_ID="<access-key-id>"
export AWS_SECRET_ACCESS_KEY="<secret-access-key>"
export AWS_DEFAULT_REGION="<region>"
export KUBECONFIG="$(pwd)/envs/dev/kubeconfig_kaos-2-eks-cluster"

# Optional Worker Group type settings

# Two worker group types are now available cpu-only or cpu and gpu based
# Use the following environment variables or create your own terraform.tfvars 
# by changing the following parameters

export TF_VAR_worker_groups_type=cpu_gpu|cpu_only (default: cpu_only)

# CPU Autoscaling group
export TF_VAR_cpu_min_node_count=# (default: 1)
export TF_VAR_cpu_max_node_count=# (default: 10)
export TF_VAR_cpu_desired_node_count=# (default: 2)
export TF_VAR_cpu_instance_type=######## (default: t2.small)
export TF_VAR_cpu_autoscaling_enabled=true|false (default: true)

# GPU Autoscaling group
export TF_VAR_gpu_min_node_count=# (default: 0)
export TF_VAR_gpu_max_node_count=# (default: 1)
export TF_VAR_gpu_desired_node_count=# (default: 2)
export TF_VAR_gpu_instance_type=######## (default: p2.xlarge)
export TF_VAR_gpu_autoscaling_enabled=true|false (default: true)
```

### Tests
To be able to run the tests you need to have the file ``secrets.yml`` in the path ``infrastructure/aws/test/integration/default``.
```bash
region: eu-west-1
aws_access_key_id: XXXXXXXXXXXXXXXXXXXX
aws_secret_access_key: XXXXXXXXXXXXXXXXXXXX
```
Then, you can type the following commands in directory ```instrastructure/aws```
````bash
kitchen converge
kitchen verify
kitchen destroy

or 

kitchen test
````

### Accessing the Cluster
To access the Kubernetes cluster on AWS, one needs to update the kubeconfig file. By default, a config file is generated
for the environment the cluster is deployed to in that respective folder. However, at times, one needs to share the cluster with other team members, in which case, it is possible to pull the config file directly from AWS. The following command can be used for that purpose.

```bash
$ aws eks update-kubeconfig --name kaos-2-{env}-eks-cluster --region {region}
```

Last but not the least, AWS uses the ConfigMap to map the users to cluster. Hence, in the best interests, one needs to add the users manually to the cluster. This is relatively simple and straightforward. The ConfigMap can be found in the 
environment to which the cluster was deployed. It would follow the following pattern: *config-map-aws-auth_kaos-2-{env}-eks-cluster.yaml*

Then one needs to add the following under *mapUsers* section. Make sure to add the team member to the group systems:masters.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::{account_id}:role/kaos-2-dev-eks-cluster20190709131031466800000007
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
  mapUsers: |
    - userarn: arn:aws:iam::{account_id}:user/{username}
      username: {username}
      groups:
        - system:masters

  mapAccounts: |
```

Once the changes have been made, one needs to apply the changes

```bash
kubectl apply -f config-map-aws-auth_kaos-2-{env}-eks-cluster.yaml
```

Here, the env refers to the name of the deployment, and can be one of dev, stage and prod.

[aws_authenticator]: https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html
