# Local

A local cluster is included for rapid prototyping, debugging and non-production work. Currently two local deployment options are available – [Docker Desktop](https://docs.docker.com/docker-for-mac/#kubernetes) and [Minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/). It is **strongly** advised to use Docker Desktop, since Minikube is **only** included for running integration tests.

> **Attention to resource handling is required when deploying a local kaos cluster since performance is directly linked to available isolated resources \(within Docker\).**

{% hint style="success" %}
It only takes approximately **1 minute** to successfully deploy a **local** kaos cluster
{% endhint %}

### Docker Desktop

A correctly running local kubernetes cluster is **absolutely** necessary prior to deploying kaos. The following steps are required before building kaos.

#### 1\) Local Kubernetes Cluster

A local kubernetes cluster within Docker Desktop must be **enabled.**

![](../../.gitbook/assets/image%20%2840%29.png)

{% hint style="warning" %}
Docker Desktop **does not** enable a Kubernetes cluster by default
{% endhint %}

The following resource requirements are **suggested** for running the Quick Start locally.

![](../../.gitbook/assets/image%20%2824%29.png)

**2\) Set Kubernetes Context**

Kubernetes conveniently organizes groups of configuration parameters under a specific name, a **context**, in order to communicate with the desired cluster. Therefore, the correct cluster context associated with Docker Desktop **needs** to be set.

```text
$ kubectl config current-context

docker-desktop
```

{% hint style="success" %}
**Success!** Kubernetes is set to communicate with Docker Desktop.
{% endhint %}

A **successfully** running local cluster with Docker Desktop will yield the following response.

```bash
$ kubectl get all

NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   2m
```

Lastly, a **local** kaos cluster with **Docker Desktop** is built and destroyed as follows.

```bash
kaos build -c DOCKER -v
kaos destroy -c DOCKER -v
```

### Minikube

{% hint style="warning" %}
**Only used for running integration tests -** use Docker Desktop for deploying a local cluster
{% endhint %}

kaos can be built and destroyed within **minikube** with the following commands.

```bash
kaos build -c MINIKUBE -v
kaos destroy -c MINIKUBE -v
```

The running kaos backend endpoint \(via ambassador as an API gateway\) can only be accessed after configuring the necessary port forwarding.

```text
kubectl port-forward svc/ambassador 30123:80 &
```

