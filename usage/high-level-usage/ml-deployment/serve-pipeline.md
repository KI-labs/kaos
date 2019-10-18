---
description: Source Bundle + Model = Running Endpoint
---

# Serve Pipeline

The **Serve Pipeline** consists of two stages - **Build** and **Serve**. They are separate Pachyderm pipelines but are linked together to form a cohesive process. The user is able to identify and track progress \(and logs\) throughout both the **Build** and **Serve** stages of the **Serve Pipeline**. Progress is shown via`kaos serve list`, while logs are available via `kaos serve logs` and `kaos serve build-logs`.

![simplified Serve Pipeline](../../../.gitbook/assets/image%20%2822%29.png)

## Inputs

The Serve Pipeline requires **both** a valid **source bundle** and **trained model** for running inference.

### Source Bundle

The source bundle is nearly identical to the source bundle described in [Train Pipeline](train-pipeline.md#source-bundle). The source bundle **requires,** at minimum, the following basic structure.

```text
mnist
└── model-serve
  └── mnist
     ├── Dockerfile
     └── model
       ├── model.py
       ├── nginx.conf
       ├── predict.py
       ├── requirements.txt
       ├── serve
       ├── web-requirements.txt
       └── wsgi.py
```

### Trained Model

A trained model can be supplied in two different forms, based on its creation. The simplest approach is linking a previously trained model \(with kaos\) via `model_id`. The second option is to omit `model_id`, which assumes that the **source bundle has everything necessary to run inference**.

#### `model_id`

A `model_id` can be found from a successful training job via `kaos train info`.

### Resources \(Optional\)

Specific resources can be attached to any serve pipeline with the following options.

| Resources | kaos option | Description |
| :--- | :--- | :--- |
| Compute | `--cpu` | Float defining the desired compute \(in cores or time\) |
| Memory | `--memory` | String defining the desired memory \(**only** valid with SI suffixes\) |
| GPU | `--gpu` | Integer defining the desired graphical processing \(in cores\) |

