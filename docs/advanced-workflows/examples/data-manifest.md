# Data Manifest

This example details how to load **remote** datasets via a manifest file. The goal is to avoid handling and storing large datasets locally.

{% hint style="warning" %}
This example assumes you are a [Data Scientist](https://app.gitbook.com/@ki-labs/s/kaos/v/latest/usage/high-level-usage#kaos-personas) using kaos with a running endpoint
{% endhint %}

## Prerequisites <a id="prerequisites"></a>

The following steps are required before being able to train the MNIST model.

### Initialization <a id="initialization"></a>

The kaos ML platform is fully functional when initialized with a **running endpoint** from a System Administrator. See [Workflows](https://app.gitbook.com/@ki-labs/s/kaos/usage/high-level-usage) for more information regarding different kaos personas.

```text
kaos init -e <running_endpoint>
```

### Create a workspace <a id="create-a-workspace"></a>

A workspace is **required** within kaos for organizing multiple environments and code. Refer to [Workspaces](https://app.gitbook.com/@ki-labs/s/kaos/usage/high-level-usage/ml-deployment/workspaces) for additional information.

```text
$ kaos workspace create -n mnist

​Successfully set mnist workspace
```

### Load the MNIST template <a id="load-the-mnist-template"></a>

kaos is supplied with various templates \(including MNIST\) for ensuring simplicity in training and serving own models.

```text
$ kaos template get --name mnist

​Successfully loaded mnist template
```

## Train with Remote Data

The training pipeline **requires** at least a valid source and data bundle. The following command uses **remote** data in the form of a data manifest, opposed to **local** data. Refer to [Data Bundle](../../usage/high-level-usage/ml-deployment/train-pipeline.md#data-bundle) for additional information.

{% hint style="info" %}
The data manifest,`/templates/mnist/data_manifest_mid/data.mf`, contains links to **1000s of small files** for training. There is a tiny **debug version** containing links to 6 files in`/templates/mnist/data_manifest_micro/data.mf`
{% endhint %}

```text
kaos train deploy -s templates/mnist/model-train \
                  -m templates/mnist/data_manifest_mid/data.mf

Submitting source bundle: templates/mnist/model-train
Compressing source bundle: 100%|███████████████████████████|
 ✔ Setting source bundle: /mnist:e23a2

Submitting data manifest: templates/mnist/data
Compressing data manifest: 100%|███████████████████████████|
 ✔ Setting data manifest: /features:c6062

CURRENT TRAINING INPUTS

+------------+-----------------+-------------+
|   Image    |       Data      | Hyperparams |
+------------+-----------------+-------------+
|     ⨂      |        ✔        |      ✗      |
| <building> | /features:c6062 |             |
+------------+-----------------+-------------+
```

