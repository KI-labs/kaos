# local

### Requirements
[Docker Desktop][docker_desktop] is an application for MacOS and Windows machines, delivering the easiest and fastest way to build production-ready container applications for Kubernetes or Swarm, working with any framework and language and targeting any platform. Build and test Linux and Windows applications and easily share them with others, bundling the code and configuration in a lightweight, portable Docker container application that runs the same everywhere.

Note that the local deployment does **not** currently work with [minikube][minikube].

A correct installation ([MacOS][MacOS] or [Windows][Windows]) will yield the following service upon activating a Kubernetes cluster.

```bash
$ kubectl get all

NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   31d
```

### Usage
The basic terraform workflow previously explained is followed for local deployment.

#### terraform init

```bash
$ terraform init

Initializing modules...
- module.ml_platform
- module.docker_build
  Getting source "../modules/docker_build"
- module.output_config
  Getting source "../modules/output_config"

Initializing provider plugins...
- Checking for available provider plugins on https://releases.hashicorp.com...
- Downloading plugin for provider "external" (1.1.2)...
- Downloading plugin for provider "local" (1.2.2)...
- Downloading plugin for provider "template" (2.1.2)...
- Downloading plugin for provider "kubernetes" (1.7.0)...
- Downloading plugin for provider "null" (2.1.2)...

Terraform has been successfully initialized!

```

#### terraform plan

```bash
$ terraform plan

Refreshing Terraform state in-memory prior to plan...
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.

data.external.md5[1]: Refreshing state...
data.external.md5[0]: Refreshing state...

------------------------------------------------------------------------

An execution plan has been generated and is shown below.

...
...
...

Plan: 21 to add, 0 to change, 0 to destroy.

```

#### terraform apply
```bash
$ terraform apply

...
...
...

Apply complete! Resources: 21 added, 0 changed, 0 destroyed.

Outputs:

backend_domain = [
    {
        hostname = localhost,
        ip =
    }
]
backend_port = 80
```

[MacOS]:https://docs.docker.com/docker-for-mac/
[Windows]:https://docs.docker.com/docker-for-windows/
[docker_desktop]: https://www.docker.com/products/docker-desktop
[minikube]: https://github.com/kubernetes/minikube
