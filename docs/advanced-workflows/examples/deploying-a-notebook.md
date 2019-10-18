# Deploying a Notebook

This example highlights the [Non-Production](../../usage/environments.md#non-production) environment within kaos.

{% hint style="warning" %}
This example assumes you are a [Data Scientist](https://app.gitbook.com/@ki-labs/s/kaos/v/latest/usage/high-level-usage#kaos-personas) using kaos with a running endpoint
{% endhint %}

## Prerequisites <a id="prerequisites"></a>

The following steps are required before being able to deploy a hosted notebook. Details on the Notebook Pipeline internals can be found [here](../../usage/high-level-usage/ml-deployment/notebook-pipeline.md).

### Initialization <a id="initialization"></a>

The kaos ML platform is fully functional when initialized with a **running endpoint** from a System Administrator. See [Workflows](https://app.gitbook.com/@ki-labs/s/kaos/v/latest/usage/high-level-usage) for more information regarding different kaos personas.

```text
kaos init -e <running_endpoint>
```

### Create a workspace <a id="create-a-workspace"></a>

A workspace is **required** within kaos for organizing multiple environments and code. Refer to [Workspaces](https://app.gitbook.com/@ki-labs/s/kaos/v/latest/usage/high-level-usage/ml-deployment/workspaces) for additional information.

```text
$ kaos workspace create -n local

Successfully set local workspace
```

## 1. Deploy a basic notebook

kaos provides a basic no-frills hosted notebook via `kaos notebook deploy`. It is the ideal approach to quickly and easily having an experimental ML environment. Keep note of the **token** for accessing the notebook \(upon receiving the running url\).

```text
$ kaos notebook deploy

 ✔ Notebook deployed - check status with kaos notebook list
Please use "jfriedman" as the notebook token
```

{% hint style="info" %}
The status of the notebook can be queried with `kaos notebook list`
{% endhint %}

The status of the notebook provides information regarding its creation, author, name, state and url. The notebook can be accessed when the state indicates `PIPELINE_RUNNING`.

```text
$ kaos notebook list

+----------------------------------------------------------------------------------------------------------------------------------------+
|                                                                RUNNING                                                                 |
+-----+-------------------------------+--------------------------+------------------+----------------------------------------+-----------+
| ind |           created_at          |           name           |      state       |                  url                   |    user   |
+-----+-------------------------------+--------------------------+------------------+----------------------------------------+-----------+
|  0  | Mon, 29 Jul 2019 19:35:55 GMT | notebook-local-jfriedman | PIPELINE_RUNNING | localhost/notebook-local-jfriedman/lab | jfriedman |
+-----+-------------------------------+--------------------------+------------------+----------------------------------------+-----------+

```

### Resulting Notebook

Connecting to the presented url will present the following familiar landing page. Note that the **token** was previously displayed when deploying the notebook \(i.e. `jfriedman`\).

![localhost/notebook-local-jfriedman/lab](../../.gitbook/assets/image%20%2834%29.png)

The resulting basic notebook is as advertised - free of any code, data and/or requirements. Files can still be added by either dragging and dropping into the browser or by following the `File/<Open from Path>` option.

![hosted notebook python3 kernel](../../.gitbook/assets/image%20%2823%29.png)

{% hint style="success" %}
kaos deploys **basic notebooks** for experimentation with one simple command
{% endhint %}

## 2. Deploy a custom notebook

The [previously](deploying-a-notebook.md#1-deploy-a-basic-notebook) explained basic notebook is slightly limiting when specific packages or large amounts of code and/or data are desired. For this reason, kaos also supports custom notebooks based on the same structure as a [source bundle](../../usage/high-level-usage/ml-deployment/train-pipeline.md#source-bundle).

A custom template is provided within kaos to ensure deploying an experimental environment is extremely straightforward. The template can be accessed as follows.

```text
$ kaos template get --name notebook

Successfully loaded notebook template
```

The same `kaos notebook deploy` command with an optional `--source_bundle` option allows a more custom experimental ML environment. Once again, please keep note of the **token** for accessing the notebook \(upon receiving the running url\).

```text
$ kaos notebook deploy -s templates/notebook

Submitting source bundle: templates/notebook
Compressing data bundle: 100%|███████████████████████████|

 ✔ Notebook deployed - check status with kaos notebook list
Please use "jfriedman" as the notebook token
```

The notebook can be accessed when the state indicates `PIPELINE_RUNNING`.

```text
$ kaos notebook list

+----------------------------------------------------------------------------------------------------------------------------------------+
|                                                                RUNNING                                                                 |
+-----+-------------------------------+--------------------------+------------------+----------------------------------------+-----------+
| ind |           created_at          |           name           |      state       |                  url                   |    user   |
+-----+-------------------------------+--------------------------+------------------+----------------------------------------+-----------+
|  0  | Mon, 29 Jul 2019 19:56:48 GMT | notebook-local-jfriedman | PIPELINE_RUNNING | localhost/notebook-local-jfriedman/lab | jfriedman |
+-----+-------------------------------+--------------------------+------------------+----------------------------------------+-----------+
```

### Resulting Notebook

The same landing page will greet upon connection. Note that the **token** was previously displayed when deploying the notebook \(i.e. `jfriedman`\). The difference is that `numpy` was added to the `requirements.txt` when building the notebook, enabling direct access to the package.

![hosted notebook python3 kernel with numpy package](../../.gitbook/assets/image%20%2819%29.png)

{% hint style="success" %}
kaos deploys **custom notebooks** for experimentation with one simple command
{% endhint %}

### Adding Data

The custom notebook also contains a useful `example_notebook.ipynb` for accessing data loaded by kaos. The "abbreviated" MNIST dataset is used to show how data is attached to a running notebook.

```text
$ kaos notebook deploy -d templates/mnist/data

Attaching data bundle: templates/mnist/data
Compressing data bundle: 100%|███████████████████████████|
```

The resulting `templates/mnist/data` directory is immediately attached and ready for experimentation within the hosted notebook.

![](../../.gitbook/assets/image%20%282%29.png)

{% hint style="success" %}
kaos can **attach any data** to a running notebook via `kaos notebook deploy`
{% endhint %}

