# Incremental Model Training

This example highlights one of the main reasons for kaos' development - [Incremental Development](../../motivation/incremental-development.md).

{% hint style="warning" %}
This example assumes you are a [Data Scientist](../../usage/high-level-usage/#kaos-personas) using kaos with a running endpoint
{% endhint %}

## Prerequisites

The following steps are required before being able to train the MNIST model.

### Initialization

The kaos ML platform is fully functional when initialized with a **running endpoint** from a System Administrator. See [Workflows](../../usage/high-level-usage/) for more information regarding different kaos personas.

```bash
kaos init -e <running_endpoint>
```

### Create a workspace

A workspace is **required** within kaos for organizing multiple environments and code. Refer to [Workspaces](../../usage/high-level-usage/ml-deployment/workspaces.md) for additional information.

```text
$ kaos workspace create -n mnist

Successfully set mnist workspace
```

### Load the MNIST template

kaos is supplied with various templates \(including MNIST\) for ensuring simplicity in training and serving own models.

```text
$ kaos template get --name mnist

Successfully loaded mnist template
```

## 1. Deploy an "initial" training job

The training pipeline **requires** at least a valid source and data bundle. Refer to [Train Pipeline](../../usage/high-level-usage/ml-deployment/train-pipeline.md) for additional information.

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

{% hint style="info" %}
The status of the training job can be queried with `kaos train list`
{% endhint %}

### Training Status

#### Building

The first stage of the [Train Pipeline](../../usage/high-level-usage/ml-deployment/train-pipeline.md) requires building the source bundle into a Docker image.

```text
+-------------------------------------------------------------------------------------------+
|                                          BUILDING                                         |
+----------+----------------------------------+-------------------------------+-------------+
| duration |              job_id              |            started            |    state    |
+----------+----------------------------------+-------------------------------+-------------+
|    ?     | 421b0ff892fc45a49a81b14eb0a734d5 | Mon, 29 Jul 2019 09:18:20 GMT | JOB_RUNNING |
+----------+----------------------------------+-------------------------------+-------------+
```

#### Training

The second stage of the [Train Pipeline](../../usage/high-level-usage/ml-deployment/train-pipeline.md) runs `./train` on the newly created Docker image.

```text
+------------------------------------------------------------------------------------------------------------+
|                                                  TRAINING                                                  |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
| ind | duration | hyperopt |              job_id              |            started            |    state    |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
|  0  |    ?     |    ?     | e58501ab0c094a8e829add97e0d23912 | Mon, 29 Jul 2019 09:19:46 GMT | JOB_RUNNING |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
```

A **successfully** trained model in kaos will yield the following output:

```text
+------------------------------------------------------------------------------------------------------------+
|                                                  TRAINING                                                  |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
| ind | duration | hyperopt |              job_id              |            started            |    state    |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
|  0  |   187    |  False   | e58501ab0c094a8e829add97e0d23912 | Mon, 29 Jul 2019 09:19:46 GMT | JOB_SUCCESS |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
```

### Training Information

Information regarding the inputs, outputs and **available** metrics can be identified with `kaos train info`.

```text
$ kaos train info -i 0

    Job ID: e58501ab0c094a8e829add97e0d23912
    Process time: 184s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'metrics_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'accuracy_test']

    Page count: 1
    Page ID: 0
+-----+--------------------+-----------------------+--------------------+-------------+-------+
| ind |        Code        |          Data         |      Model ID      | Hyperparams | Score |
+-----+--------------------+-----------------------+--------------------+-------------+-------+
|  0  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d:cebf65 |     None    |  1.0  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                    |             |       |
+-----+--------------------+-----------------------+--------------------+-------------+-------+
```

A specific metric can be displayed using  the `--sort_by` option in `kaos train info`.

```text
$ kaos train info -i 0 -s accuracy_test

    Job ID: e58501ab0c094a8e829add97e0d23912
    Process time: 184s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'metrics_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'accuracy_test']

    Page count: 1
    Page ID: 0
+-----+--------------------+-----------------------+--------------------+-------------+-------------------+
| ind |        Code        |          Data         |      Model ID      | Hyperparams |       Score       |
+-----+--------------------+-----------------------+--------------------+-------------+-------------------+
|  0  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d:cebf65 |     None    | 0.867704280155642 |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                    |             |                   |
+-----+--------------------+-----------------------+--------------------+-------------+-------------------+
```

{% hint style="danger" %}
How about we adapt the `kernel` definition \(see [Vector Classification](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html)\) in hopes of improving the test accuracy - currently at **86.7%**
{% endhint %}

## 2. Adapt the model definition

Changing the `kernel` is possible by altering the `mnist/model-train/mnist/model/train` script.

```python
    # Model definition and classification
    classifier = svm.SVC(gamma=float(params['gamma']),
        decision_function_shape=params['decision_function_shape'],
        kernel='linear',
        degree=int(params['degree']))
```

Training a new model with the updated `kernel` is **run with the exact same command** in kaos.

```text
$ kaos train deploy -s templates/mnist/model-train

Submitting source bundle: templates/mnist/model-train
Compressing source bundle: 100%|███████████████████████████|
 ✔ Setting source bundle: /mnist:7620b

CURRENT TRAINING INPUTS

+------------+-----------------+-------------+
|   Image    |       Data      | Hyperparams |
+------------+-----------------+-------------+
|     ⨂      |        ✔        |      ✗      |
| <building> | /features:9fd9d |             |
+------------+-----------------+-------------+
```

Both training jobs are readily available through `kaos train list`.

```text
+------------------------------------------------------------------------------------------------------------+
|                                                  TRAINING                                                  |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
| ind | duration | hyperopt |              job_id              |            started            |    state    |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
|  0  |    75    |  False   | eb9d6b45c00140859b68a96af6e10dc4 | Mon, 29 Jul 2019 09:53:57 GMT | JOB_SUCCESS |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
|  1  |   187    |  False   | e58501ab0c094a8e829add97e0d23912 | Mon, 29 Jul 2019 09:19:46 GMT | JOB_SUCCESS |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
```

{% hint style="info" %}
The output is ordered by the **latest successfully trained model**
{% endhint %}

The **same** command for displaying the desired metric can be run \(as before\) since the latest model is first - e.g. index zero.

```text
$ kaos train info -i 0 -s accuracy_test

    Job ID: eb9d6b45c00140859b68a96af6e10dc4
    Process time: 72s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'metrics_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'accuracy_test']

    Page count: 1
    Page ID: 0
+-----+--------------------+-----------------------+--------------------+-------------+--------------------+
| ind |        Code        |          Data         |      Model ID      | Hyperparams |       Score        |
+-----+--------------------+-----------------------+--------------------+-------------+--------------------+
|  0  | Author: jfriedman  |   Author: jfriedman   | 7620b_9fd9d:8373f2 |     None    | 0.8932740411339634 |
|     | Path: /mnist:7620b | Path: /features:9fd9d |                    |             |                    |
+-----+--------------------+-----------------------+--------------------+-------------+--------------------+
```

{% hint style="danger" %}
The newly changed `kernel` improves the test accuracy to **89.3%** but there is still plenty of room for improvement by increasing the size of the "abbreviated" MNIST dataset.
{% endhint %}

## 3. Increasing the training dataset

The abbreviated MNIST training dataset was 6000 images, which is approximately **11%** of the original. An increase to 20000 images \(**36%** of the original\) will yield a much more representative training set. The new data is added to the original file `mnist/data/features/training/training_mini.csv`.

```text
$ kaos train deploy -d templates/mnist/data

Submitting data bundle: templates/mnist/data
Compressing data bundle: 100%|███████████████████████████|
 ✔ Setting data bundle: /features:7b0c8

CURRENT TRAINING INPUTS

+-------------------------+-----------------+-------------+
|          Image          |       Data      | Hyperparams |
+-------------------------+-----------------+-------------+
|            ✔            |        ✔        |      ✗      |
| build-train-mnist:7620b | /features:7b0c8 |             |
+-------------------------+-----------------+-------------+
```

Once again, the **same** command for displaying the test accuracy can be run since the latest model is first.

```text
$ kaos train info -i 0 -s accuracy_test

    Job ID: 239144244f924799b7a0eb4e1e148e17
    Process time: 347s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'metrics_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'accuracy_test']

    Page count: 1
    Page ID: 0
+-----+--------------------+-----------------------+--------------------+-------------+--------------------+
| ind |        Code        |          Data         |      Model ID      | Hyperparams |       Score        |
+-----+--------------------+-----------------------+--------------------+-------------+--------------------+
|  0  | Author: jfriedman  |   Author: jfriedman   | 7620b_7b0c8:8b03ca |     None    | 0.9588882712618121 |
|     | Path: /mnist:7620b | Path: /features:7b0c8 |                    |             |                    |
+-----+--------------------+-----------------------+--------------------+-------------+--------------------+
```

Great news, the greatly increased training dataset improved test accuracy to **95.9%**.

{% hint style="success" %}
Success! You have just witnessed the **simplicity** of incremental model development in kaos
{% endhint %}

