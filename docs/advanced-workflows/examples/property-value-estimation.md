# Debugging

Although kaos was designed and abstracted for simplicity, it still requires some form of debugging since erroneous inputs are inevitable. This example presents a few built-in approaches for debugging both training and serving jobs. 

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
$ kaos workspace create -n mnist​​

Successfully set mnist workspace
```

### Load the MNIST template <a id="load-the-mnist-template"></a>

kaos is supplied with various templates \(including MNIST\) for ensuring simplicity in training and serving own models.

```text
$ kaos template get --name mnist

​​Successfully loaded mnist template
```

## 1. Build errors

A simplistic example of a build error is presented below. In short, a typo in the `requirements.txt` file will cause an error during the build stage of the [Train Pipeline](../../usage/high-level-usage/ml-deployment/train-pipeline.md). Note that this is identical to an error during the build stage of the [Serve Pipeline](../../usage/high-level-usage/ml-deployment/serve-pipeline.md)  and Notebook Pipeline but this example will focus on **training**.

```text
scikit-learn==0.20.3
scikit-image==0.15.0
numpy==1.16.2
joblib==0.13.2
pandas=0.24
```

The training job is deployed with the erroneous source bundle.

```text
$ kaos train deploy -s templates/mnist/model-train \
                    -d templates/mnist/data

Submitting source bundle: templates/mnist/model-train
Compressing source bundle: 100%|███████████████████████████|
 ✔ Setting source bundle: /mnist:17127

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

The build stage will fail due to the incorrect definition within `requirements.txt`.

```text
$ kaos train list

+-------------------------------------------------------------------------------------------+
|                                          BUILDING                                         |
+----------+----------------------------------+-------------------------------+-------------+
| duration |              job_id              |            started            |    state    |
+----------+----------------------------------+-------------------------------+-------------+
|    20    | 7a74b6974ba346238baf0a5f397774df | Mon, 29 Jul 2019 15:08:36 GMT | JOB_FAILURE |
+----------+----------------------------------+-------------------------------+-------------+

```

Debugging kaos jobs in the building stage is completed by inspecting the job logs. This functionality is exposed through `kaos train build-logs`. 

```text
$ kaos train build-logs -j 7a74b6974ba346238baf0a5f397774df

[2019-07-29 15:08:36] processing job 7a74b6974ba346238baf0a5f397774df
[2019-07-29 15:08:36] starting to download data
[2019-07-29 15:08:36] finished downloading data after 29.638679ms
[2019-07-29 15:08:36] beginning to run user code
[2019-07-29 15:08:42] The command '/bin/sh -c if [ -f /opt/program/requirements.txt ] ; then pip3 install --no-cache-dir -r /opt/program/requirements.txt; fi' returned a non-zero code: 1
```

{% hint style="success" %}
`kaos train build-logs` provides an easy way to **retrieve logs** during the **building**
{% endhint %}

## 2. Train errors

A basic example for debugging an error during training is presented. Once again, a typo is introduced by "forgetting" to leaving an open bracket in the `train` function.

```python
def train():
   
    <do stuff>
    
    # Model definition and classification
    classifier = svm.SVC(gamma=float(params['gamma']),
                         decision_function_shape=params['decision_function_shape'],
                         kernel=params['kernel'],
                         degree=int(params['degree']))
    model = classifier.fit(training_data, training_labels.values
```

The training job is deployed with the erroneous source bundle.

```text
$ kaos train deploy -s templates/mnist/model-train \
                    -d templates/mnist/data

Submitting source bundle: templates/mnist/model-train
Compressing source bundle: 100%|███████████████████████████|
 ✔ Setting source bundle: /mnist:69d5b

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

The train stage will fail due to the error in the `train` script.

```text
$ kaos train list

+------------------------------------------------------------------------------------------------------------+
|                                                  TRAINING                                                  |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
| ind | duration | hyperopt |              job_id              |            started            |    state    |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
|  0  |    1     |  False   | 8811746e3f6343d1bd6f3d520f7a54d0 | Mon, 29 Jul 2019 15:25:45 GMT | JOB_FAILURE |
+-----+----------+----------+----------------------------------+-------------------------------+-------------+
```

Debugging kaos jobs in the training stage is completed by inspecting the job logs. This functionality is exposed through `kaos train logs`. 

```text
$ kaos train logs -j 8811746e3f6343d1bd6f3d520f7a54d0

[2019-07-29 15:25:45] processing job 8811746e3f6343d1bd6f3d520f7a54d0
[2019-07-29 15:25:45] starting to download data
[2019-07-29 15:25:45] finished downloading data after 454.07585ms
[2019-07-29 15:25:45] beginning to run user code
[2019-07-29 15:25:46]   File "./train", line 88
[2019-07-29 15:25:46]     out_path = os.path.join(model_path, 'model.pkl')
[2019-07-29 15:25:46]            ^
[2019-07-29 15:25:46] SyntaxError: invalid syntax
```

{% hint style="success" %}
`kaos train logs` provides an easy way to **retrieve logs** during **training**
{% endhint %}

## 3. Serve errors

A basic example for debugging an error during serving is presented. Once again, a typo is introduced by using an incorrect model name - `model.docx` in the `predict.py` script.

```python
ctx = load_ctx("model.docx")  # load trained model
```

The following debugging assumes a trained `model_id` exists when running `kaos train info`.

```text
$ kaos train info -i 0

    Job ID: 48c7e33df1cf48f2a649f0c674063200
    Process time: 49s
    State: JOB_SUCCESS
    Available metrics: ['accuracy_train', 'accuracy_test', 'metrics_train', 'accuracy_validation', 'metrics_validation', 'metrics_test']

    Page count: 1
    Page ID: 0
+-----+--------------------+-----------------------+--------------------+-------------+
| ind |        Code        |          Data         |      Model ID      | Hyperparams |
+-----+--------------------+-----------------------+--------------------+-------------+
|  0  | Author: jfriedman  |   Author: jfriedman   | e23a2_9fd9d:134639 |     None    |
|     | Path: /mnist:e23a2 | Path: /features:9fd9d |                    |             |
+-----+--------------------+-----------------------+--------------------+-------------+
```

The serve job is deployed with the erroneous source bundle.

```text
$ kaos serve deploy -s templates/mnist/model-serve \
                    -m e23a2_9fd9d:134639
                    
Submitting source bundle: templates/mnist/model-serve
Compressing source bundle: 100%|███████████████████████████|
 ✔ Adding trained model_id: e23a2_9fd9d:134639
 ✔ Setting source bundle: /mnist:93168
```

The status of the deployed endpoint will indicate `PIPELINE_RUNNING` since it is only a measure of the pipeline health - not any invocations.

```text
$ kaos serve list

+------------------------------------------------------------------------------------------------------------------------------------+
|                                                              RUNNING                                                               |
+-----+-------------------------------+--------------------+------------------+------------------------------------------+-----------+
| ind |           created_at          |        name        |      state       |                   url                    |    user   |
+-----+-------------------------------+--------------------+------------------+------------------------------------------+-----------+
|  0  | Mon, 29 Jul 2019 15:45:39 GMT | serve-mnist-0c9718 | PIPELINE_RUNNING | localhost/serve-mnist-0c9718/invocations | jfriedman |
+-----+-------------------------------+--------------------+------------------+------------------------------------------+-----------+
```

A simple prediction with `templates/mnist/test_payload.jpg` will yield an error.

```text
$ curl -X POST localhost/serve-mnist-0c9718/invocations \
         --data-binary @templates/mnist/test_payload.jpg

upstream connect error or disconnect/reset before headers. reset reason: connection failure
```

Debugging kaos endpoints is completed by inspecting the running flask application. This functionality is exposed through `kaos serve logs`.

```text
$ kaos serve logs -e serve-mnist-0c9718

[2019-07-29 15:45:48] starting to download data
[2019-07-29 15:45:48] processing job d6625ac8331243bcbdb7d4ec0276c8dc
[2019-07-29 15:45:48] finished downloading data after 32.712387ms
[2019-07-29 15:45:48] beginning to run user code
[2019-07-29 15:45:49] ****** Start inference server (3 workers) ******
[2019-07-29 15:45:49] [2019-07-29 15:45:49 +0000] [18] [INFO] Starting gunicorn 19.9.0
[2019-07-29 15:45:49] [2019-07-29 15:45:49 +0000] [18] [INFO] Listening at: unix:/tmp/gunicorn.sock (18)
[2019-07-29 15:45:49] [2019-07-29 15:45:49 +0000] [18] [INFO] Using worker: gevent
[2019-07-29 15:45:49] [2019-07-29 15:45:49 +0000] [22] [INFO] Booting worker with pid: 22
[2019-07-29 15:45:49] [2019-07-29 15:45:49 +0000] [24] [INFO] Booting worker with pid: 24
[2019-07-29 15:45:49] [2019-07-29 15:45:49 +0000] [25] [INFO] Booting worker with pid: 25
[2019-07-29 15:45:55] [2019-07-29 15:45:55 +0000] [22] [ERROR] Exception in worker process
[2019-07-29 15:45:55] Traceback (most recent call last):
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/arbiter.py", line 583, in spawn_worker
[2019-07-29 15:45:55]     worker.init_process()
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/workers/ggevent.py", line 203, in init_process
[2019-07-29 15:45:55]     super(GeventWorker, self).init_process()
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/workers/base.py", line 129, in init_process
[2019-07-29 15:45:55]     self.load_wsgi()
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/workers/base.py", line 138, in load_wsgi
[2019-07-29 15:45:55]     self.wsgi = self.app.wsgi()
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/app/base.py", line 67, in wsgi
[2019-07-29 15:45:55]     self.callable = self.load()
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/app/wsgiapp.py", line 52, in load
[2019-07-29 15:45:55]     return self.load_wsgiapp()
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/app/wsgiapp.py", line 41, in load_wsgiapp
[2019-07-29 15:45:55]     return util.import_app(self.app_uri)
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/gunicorn/util.py", line 350, in import_app
[2019-07-29 15:45:55]     __import__(module)
[2019-07-29 15:45:55]   File "/opt/program/wsgi.py", line 1, in <module>
[2019-07-29 15:45:55]     import predict
[2019-07-29 15:45:55]   File "/opt/program/predict.py", line 28, in <module>
[2019-07-29 15:45:55]     ctx = load_ctx("model.docx")  # load trained model
[2019-07-29 15:45:55]   File "/opt/program/model.py", line 47, in load_ctx
[2019-07-29 15:45:55]     model = joblib.load(model_path)
[2019-07-29 15:45:55]   File "/usr/local/lib/python3.5/dist-packages/joblib/numpy_pickle.py", line 590, in load
[2019-07-29 15:45:55]     with open(filename, 'rb') as f:
[2019-07-29 15:45:55] FileNotFoundError: [Errno 2] No such file or directory: 'model.docx'
```

{% hint style="success" %}
`kaos serve logs` provides an easy way to **retrieve logs** during **inference**
{% endhint %}

