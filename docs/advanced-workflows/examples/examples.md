# Hyperparameter Optimization

> In machine learning, **hyperparameter optimization** is the selection of optimal parameters for learning a specific algorithm. A hyperparameter is a parameter whose value is used as input to the learning process.

kaos supports hyperparameter optimization based on a simplistic [Grid Search](https://en.wikipedia.org/wiki/Hyperparameter_optimization#Grid_search) approach. More information regarding its implementation is explained in the [Train Pipeline](../../usage/high-level-usage/ml-deployment/train-pipeline.md#params-optional).

This example showcases the ease of selecting the best hyperparameter based on parallel training jobs with all combinations \(i.e. Grid Search\) of the user inputs.

{% hint style="warning" %}
This example assumes you are a [Data Scientist](../../usage/high-level-usage/#kaos-personas) using kaos with a running endpoint
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

## 1. Adapt training script

A hyperparameter job will function properly when the supplied `train` script exposes parameters with `params` variable. An excerpt from the template `mnist` model is shown below.

```python
def train():
    # load "static" params
    with open(params_fid, 'r') as src:
        params = json.load(src)

    # load params from "hyperopt" job
    params = hyperparams(params)

    <do stuff>

    classifier = svm.SVC(gamma=float(params['gamma']),
        decision_function_shape=params['decision_function_shape'],
        kernel=params['kernel'],
        degree=int(params['degree']))
```

Build the newly adapted training image based on the source bundle.

```text
$ kaos train deploy -s templates/mnist/model-train

Submitting source bundle: templates/mnist/model-train
Compressing source bundle: 100%|███████████████████████████|
 ✔ Setting source bundle: /mnist:e23a2

CURRENT TRAINING INPUTS

+------------+-----------------+-------------+
|   Image    |       Data      | Hyperparams |
+------------+-----------------+-------------+
|     ⨂      |        ✗        |      ✗      |
| <building> |                 |             |
+------------+-----------------+-------------+
```

## 2. Define hyperparameters

The structure of valid hyperparameters is a simple JSON with the correct keys \(as per `train`\).

```javascript
{
  "degree": [
    3,
    5
  ],
  "kernel": [
    "linear",
    "poly"
  ],
  "gamma": [
    10,
    0.1,
    0.01
  ]
}
```

## 3. Deploy all hyperparameter jobs

Running **parallel** hyperparameter jobs is done through the exact same command for running a normal training job - `kaos train deploy`. Note that running `--help` further describes the additional options.

```text
$ kaos train deploy -d templates/mnist/data \
                    -h templates/mnist/hyperopt/params.json \
                    -p 2

Submitting data bundle: templates/mnist/data
Compressing data bundle: 100%|███████████████████████████|
 ✔ Setting data bundle: /features:9fd9d

 Submitting hyperparams bundle: templates/mnist/hyperopt/params.json
 ✔ Setting hyperparameters bundle: /3fbf2/*

CURRENT HYPERPARAMETERS (12)

+-----+--------+-------+--------+
| ind | degree | gamma | kernel |
+-----+--------+-------+--------+
|  0  |   3    |   10  | linear |
+-----+--------+-------+--------+
|  1  |   3    |  0.1  | linear |
+-----+--------+-------+--------+
|  2  |   3    |  0.01 | linear |
+-----+--------+-------+--------+
|  3  |   3    |   10  |  poly  |
+-----+--------+-------+--------+
|  4  |   3    |  0.1  |  poly  |
+-----+--------+-------+--------+
|  5  |   3    |  0.01 |  poly  |
+-----+--------+-------+--------+
|  6  |   5    |   10  | linear |
+-----+--------+-------+--------+
|  7  |   5    |  0.1  | linear |
+-----+--------+-------+--------+
|  8  |   5    |  0.01 | linear |
+-----+--------+-------+--------+
|  9  |   5    |   10  |  poly  |
+-----+--------+-------+--------+
|  10 |   5    |  0.1  |  poly  |
+-----+--------+-------+--------+
|  11 |   5    |  0.01 |  poly  |
+-----+--------+-------+--------+

CURRENT TRAINING INPUTS

+-------------------------+-----------------+-------------+
|          Image          |       Data      | Hyperparams |
+-------------------------+-----------------+-------------+
|            ✔            |        ✔        |      ✔      |
| build-train-mnist:e23a2 | /features:9fd9d |   /3fbf2/*  |
+-------------------------+-----------------+-------------+
```

{% hint style="warning" %}
The resulting **queued training jobs** are identified upon submission to kaos
{% endhint %}

## 4. Select optimal hyperparameter

Information from a specifc training job can be found via `kaos train info`. It includes all inputs, outputs and **available** metrics.

```text
$ kaos train info -i 0

    Job ID: 679823be5409498093dc2e229084f8db
    Process time: 846s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'metrics_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'accuracy_test']

    Page count: 2
    Page ID: 0
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
| ind |        Code        |          Data         |         Model ID         |                     Hyperparams                     |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  0  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:776614 |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |   Path: /3fbf2/degree=5_kernel=poly_gamma=0.1.json  |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  1  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:f94840 |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=3_kernel=poly_gamma=0.01.json  |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  2  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:c064e1 |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |   Path: /3fbf2/degree=3_kernel=poly_gamma=10.json   |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  3  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:057495 |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=3_kernel=linear_gamma=10.json  |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  4  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:f5bddc |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          | Path: /3fbf2/degree=3_kernel=linear_gamma=0.01.json |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  5  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:12060d |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=3_kernel=linear_gamma=0.1.json |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  6  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:c6ca87 |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=5_kernel=linear_gamma=0.1.json |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  7  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:f87b62 |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |   Path: /3fbf2/degree=3_kernel=poly_gamma=0.1.json  |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  8  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:5920b9 |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=5_kernel=linear_gamma=10.json  |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
|  9  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:84e67d |                  Author: jfriedman                  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=5_kernel=poly_gamma=0.01.json  |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+
```

{% hint style="warning" %}
Note that kaos **results are paginated** if exceeding 10 trained models within a single job
{% endhint %}

A specific metric can be displayed using the `--sort_by` option in `kaos train info`. For this example, the **best** hyperparameter set is determined based on `accuracy_validation`.

```text
$ kaos train info -i 0 -s accuracy_validation


    Job ID: 679823be5409498093dc2e229084f8db
    Process time: 513s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'metrics_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'accuracy_test']

    Page count: 2
    Page ID: 0
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
| ind |        Code        |          Data         |         Model ID         |                     Hyperparams                     |       Score        |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  0  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:f94840 |                  Author: jfriedman                  | 0.9394107837687604 |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=3_kernel=poly_gamma=0.01.json  |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  1  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:c064e1 |                  Author: jfriedman                  | 0.9394107837687604 |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |   Path: /3fbf2/degree=3_kernel=poly_gamma=10.json   |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  2  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:f87b62 |                  Author: jfriedman                  | 0.9394107837687604 |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |   Path: /3fbf2/degree=3_kernel=poly_gamma=0.1.json  |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  3  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:057495 |                  Author: jfriedman                  |  0.90550305725403  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=3_kernel=linear_gamma=10.json  |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  4  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:f5bddc |                  Author: jfriedman                  |  0.90550305725403  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          | Path: /3fbf2/degree=3_kernel=linear_gamma=0.01.json |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  5  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:12060d |                  Author: jfriedman                  |  0.90550305725403  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=3_kernel=linear_gamma=0.1.json |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  6  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:c6ca87 |                  Author: jfriedman                  |  0.90550305725403  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=5_kernel=linear_gamma=0.1.json |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  7  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:5920b9 |                  Author: jfriedman                  |  0.90550305725403  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |  Path: /3fbf2/degree=5_kernel=linear_gamma=10.json  |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  8  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:abe93e |                  Author: jfriedman                  |  0.90550305725403  |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          | Path: /3fbf2/degree=5_kernel=linear_gamma=0.01.json |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
|  9  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d_3fbf2:776614 |                  Author: jfriedman                  | 0.8615897720956087 |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                          |   Path: /3fbf2/degree=5_kernel=poly_gamma=0.1.json  |                    |
+-----+--------------------+-----------------------+--------------------------+-----------------------------------------------------+--------------------+
```

The above table indicates that the best set of hyperparameters are the following. Note that the validation set appears to be insenstive to `gamma`, likely due to the reduced dataset size and distribution.

| Parameter | Value |
| :--- | :--- |
| Degree | **3** |
| Kernel | **poly** |
| Gamma | **10** |

{% hint style="success" %}
Success! You have just run a **parallelized hyperparameter optimization** in kaos
{% endhint %}

