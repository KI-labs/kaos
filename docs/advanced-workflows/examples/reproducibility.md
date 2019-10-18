# Reproducibility

This example highlights one of the main reasons for kaos' development - [Reproducibility](../../motivation/reproducibility.md).

{% hint style="warning" %}
This example assumes you are a [Data Scientist](https://app.gitbook.com/@ki-labs/s/kaos/usage/high-level-usage#kaos-personas) using kaos with a running endpoint
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

### Deploy an "initial" training job

The training pipeline **requires** at least a valid source and data bundle. Refer to [Train Pipeline](https://app.gitbook.com/@ki-labs/s/kaos/usage/high-level-usage/ml-deployment/train-pipeline) for additional information.

```text
$ kaos train deploy -s templates/mnist/model-train \
                    -d templates/mnist/data

Submitting source bundle: templates/mnist/model-train
Compressing source bundle: 100%|███████████████████████████|
 ✔ Setting source bundle: /mnist:e23a2

Submitting data bundle: templates/mnist/data
Compressing data bundle: 100%|███████████████████████████|
 ✔ Setting data bundle: /features:9fd9d

CURRENT TRAINING INPUTS

+------------+-----------------+-------------+
|   Image    |       Data      | Hyperparams |
+------------+-----------------+-------------+
|     ⨂      |        ✔        |      ✗      |
| <building> | /features:9fd9d |             |
+------------+-----------------+-------------+
```

The prerequisites are complete when the training job state is `JOB_SUCCESS`. Below is the desired output.

```text
$ kaos train list

+------------------------------------------------------------------------------------------------------------+
|                                                  TRAINING                                                  |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
| ind | duration | hyperopt |              job_id              |            started            |    state    |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
|  0  |    71    |  False   | 1ed80bcad9a6465db67652255f904377 | Mon, 29 Jul 2019 12:38:39 GMT | JOB_SUCCESS |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
```

## 1. Reproduce training

kaos allows any user \(within the correct workspace\) to retrieve a previously trained model. The following approach is the ideal method for **inspecting artifacts** or **collaborative training** \(i.e. retraining a colleague's model\). kaos ensure simplicity for redeployment since it maintains the original bundle structure.

### Retrieve train artifacts

#### Code

kaos is able to retrieve the [**source bundle**](../../usage/high-level-usage/ml-deployment/train-pipeline.md#source-bundle) used for training with the following command.

```text
$ kaos train get -i 0 -c

Extracting train bundle: /mnist/1ed80bcad9a6465db67652255f904377
Extracting train bundle: 100%|███████████████████████████|
```

The source bundle \(i.e. **code**\) is extracted in the following structure.

```text
$ tree mnist

mnist
└── 1ed80bcad9a6465db67652255f904377
   └── code
      └── mnist:e23a2
         ├── Dockerfile
         └── model
            ├── params.json
            ├── requirements.txt
            ├── train
            └── utils.py

```

{% hint style="success" %}
kaos **simplifies retraining** by running `kaos train deploy` after `kaos train get` 
{% endhint %}

#### Data

kaos is able to retrieve the [**data bundle**](../../usage/high-level-usage/ml-deployment/train-pipeline.md#data-bundle) used for training with the following command.

```text
$ kaos train get -i 0 -d

Extracting train bundle: /mnist/1ed80bcad9a6465db67652255f904377
Extracting train bundle: 100%|███████████████████████████|
```

The source bundle \(i.e. **data**\) is extracted based on the supplied input format.

```text
$ tree mnist

mnist
└── 1ed80bcad9a6465db67652255f904377
   └── data
      └── features:9fd9d
         ├── test
         │  └── test_mini.csv
         ├── training
         │  └── training_mini.csv
         └── validation
            └── validation_mini.csv
```

#### Model

kaos is able to retrieve all [**output**](../../usage/high-level-usage/ml-deployment/train-pipeline.md#output) from training with the following command.

```text
$ kaos train get -i 0 -m

Extracting train bundle: /mnist/1ed80bcad9a6465db67652255f904377
Extracting train bundle: 100%|███████████████████████████|
```

**Outputs** are extracted based on the template output - `/model` and `/metrics`.

```text
$ tree mnist

mnist
└── 1ed80bcad9a6465db67652255f904377
   └── models
      └── b82151
         ├── metrics
         │  └── metrics.json
         └── model
            └── model.pkl
```

{% hint style="success" %}
kaos ensures **full reproducibility** of any previous training job
{% endhint %}

### Identify model provenance

Reproducibility of a model is also a function of understand how the output was created - its **provenance**. This information is readily available for any user \(within the correct workspace\). The [direct acyclic graph \(DAG\)](https://en.wikipedia.org/wiki/Directed_acyclic_graph) associated with a specific training job can be visualized via `kaos train provenance`. Note that the required `model_id` is found with `kaos train info`.

```text
$ kaos train info -i 0

    Job ID: 1ed80bcad9a6465db67652255f904377
    Process time: 67s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'metrics_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'accuracy_test']

    Page count: 1
    Page ID: 0
+-----+--------------------+-----------------------+--------------------+-------------+
| ind |        Code        |          Data         |      Model ID      | Hyperparams |
+-----+--------------------+-----------------------+--------------------+-------------+
|  0  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d:b82151 |     None    |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                    |             |
+-----+--------------------+-----------------------+--------------------+-------------+

$ 
```

In short, running `kaos train provenance -m e23a2_9fd9d:b82151` yields the visual overview \(below\) of the entire training provenance.

![mnist/provenance/model-e23a2\_9fd9d:b82151.pdf](../../.gitbook/assets/image%20%281%29.png)

{% hint style="success" %}
kaos tracks **training** provenance to keep all processing **fully transparent**
{% endhint %}

## 2. Reproduce serving

Deploying a **running endpoint** requires the `model_id` from above \(e.g. `e23a2_9fd9d:b82151` \). Refer to [Serve Pipeline](../../usage/high-level-usage/ml-deployment/serve-pipeline.md) for additional information.

```text
$ kaos serve deploy -s templates/mnist/model-serve \
                    -m e23a2_9fd9d:b82151

Submitting source bundle: templates/mnist/model-serve
Compressing source bundle: 100%|███████████████████████████|
 ✔ Adding trained model_id: e23a2_9fd9d:b82151
 Compressing Source Bundle: 100%|███████████████████████████|
 ✔ Setting source bundle: /mnist:ff06b
```

{% hint style="info" %}
The status of deploying the endpoint can be queried with `kaos serve list`
{% endhint %}

### Retrieve serve artifacts

#### Code

kaos is able to retrieve the [**source bundle**](../../usage/high-level-usage/ml-deployment/serve-pipeline.md#source-bundle) used for serving with the following command.

```text
$ kaos serve get -i 0

Extracting serve bundle: /mnist/serve-mnist-ae6466
Extracting serve bundle: 100%|███████████████████████████|
```

The source bundle \(i.e. **code**\) is extracted in the following structure.

```text
$ tree mnist

mnist
└── serve-mnist-ae6466
   └── code
      └── mnist:ff06b
         ├── Dockerfile
         └── model
            ├── model.pkl
            ├── model.py
            ├── nginx.conf
            ├── predict.py
            ├── requirements.txt
            ├── serve
            ├── web-requirements.txt
            └── wsgi.py

```

{% hint style="success" %}
kaos **simplifies updating endpoints** by running `kaos serve deploy` after `kaos serve get`
{% endhint %}

### Identify endpoint provenance

Reproducibility of a running endpoint is extremely difficult given the processing chain from training to serving. kaos simplifies the entire process with **full** **provenance** based on a running endpoint**.**

```text
$ kaos serve list

+------------------------------------------------------------------------------------------------------------------------------------+
|                                                              RUNNING                                                               |
+-----+-------------------------------+--------------------+------------------+------------------------------------------+-----------+
| ind |           created_at          |        name        |      state       |                   url                    |    user   |
+-----+-------------------------------+--------------------+------------------+------------------------------------------+-----------+
|  0  | Mon, 29 Jul 2019 13:20:22 GMT | serve-mnist-ae6466 | PIPELINE_RUNNING | localhost/serve-mnist-ae6466/invocations | jfriedman |
+-----+-------------------------------+--------------------+------------------+------------------------------------------+-----------+
```

Running `kaos serve provenance -e serve-mnist-ae6466` yields a visual overview \(below\) of the entire endpoint provenance \(i.e. both training and serving and their respective inputs\).

![mnist/provenance/serve-mnist-ae6466.pdf](../../.gitbook/assets/image%20%2848%29.png)

{% hint style="success" %}
kaos tracks **endpoint** provenance to keep all processing **fully transparent**
{% endhint %}

