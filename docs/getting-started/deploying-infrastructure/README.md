# Deploying Infrastructure

{% hint style="warning" %}
This section is only for [**System Administrators**](../../usage/high-level-usage/#kaos-personas) and [**Superheros**](../../usage/high-level-usage/#kaos-personas)
{% endhint %}

{% hint style="danger" %}
Note that only **a single backend** can be deployed from the same directory. **Destroying** the current backend or **switching directories** is required to build a second backend.
{% endhint %}

## Requirements

kaos is cloud agnostic, meaning it can be deployed in **all** major cloud providers. The following sections highlight the required `ENV` by cloud.

```bash
export KAOS_HOME="<path/to/local/cloned/kaos>"
```

{% hint style="danger" %}
Note that ENV`KAOS_HOME` is **required irrespective of cloud provider.**
{% endhint %}

## Infrastructure Backends

The current version of kaos supports both [**Local**](local.md) and [**Cloud**](cloud.md) deployments.

{% page-ref page="local.md" %}

{% page-ref page="cloud.md" %}

Deploying infrastructure \(regardless of location\) is completed with the same command - `kaos build`. All available options are shown below.

```text
Usage: kaos build [OPTIONS]

Options:
  -c, --cloud [DOCKER|MINIKUBE|AWS|GCP]
                                  selected provider provider  [required]
  -e, --env [prod|stage|dev]      selected infrastructure environment
  -f, --force                     force building infrastructure
  -v, --verbose                   verbose output
  -y, --yes                       answer yes to any prompt
  -l, --local_backend             terraform will store backend locally, only
                                  relevant for clouds
  --help                          Show this message and exit.
```

{% hint style="info" %}
Note that building the backend can be done in any folder **assuming** export of `KAOS_HOME`.
{% endhint %}

A successfully created running endpoint can be shared with Data Scientists for use in `kaos init`. See [here](../../usage/high-level-usage/infrastructure-deployment.md#sharing-running-endpoint) for detailed instructions on how to share the endpoint.

## Infrastructure Environments

kaos provides the ability to build **multiple** unique environments within a **single** infrastructure. The approach allows for independent cluster settings within the same infrastructure \(i.e. to preserve data locality\). For instance, it enables the [System Admin](../../usage/high-level-usage/#kaos-personas) or [Superhero](../../usage/high-level-usage/#kaos-personas) to build two different clusters for handling different computational needs \(i.e. `cpu` vs. `gpu`\). kaos supports the following **three** **distinct** environments:

* Development \(`--env dev`\)
* Staging \(`--env stage`\)
* Production \(`--env prod`\)

{% hint style="info" %}
There is **no actual difference** between deploying a `prod` vs. a `dev` cluster within kaos **unless inputs are properly defined** \(via ENVs\). They simply allow the creation of **multiple unique environments within a single infrastructure**.
{% endhint %}

{% hint style="danger" %}
Local infrastructure backends **do not support** environments!
{% endhint %}

