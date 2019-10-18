# States

Pipelines and job within kaos rely on [Pachyderm](https://pachyderm.github.io/), which uses the following descriptions for distinguishing different states.

### Training Jobs \(and all Build Jobs\)

The following states are valid when deploying a **training** **job** in kaos.

| State | Description |
| :--- | :--- |
| **`JOB_STARTING`** | Job _initialized_ with inputs \(i.e. source and data bundle\) |
| **`JOB_RUNNING`** | Job _running_ based on process \(i.e. train vs. build\) |
| **`JOB_MERGED`** | Job in _merging_ state prior to completion |
| **`JOB_SUCCESS`** | Job _successfully_ completed |
| **`JOB_FAILURE`** | Job _failed_ - check logs |
| **`JOB_KILLED`** | Job _killed_ by user |

### Serve Pipelines

The following states are valid when deploying a **serve** **pipeline** in kaos.

| State | Description |
| :--- | :--- |
| **`PIPELINE_STANDBY`** | Serve pipeline _awaiting_ inputs |
| **`PIPELINE_STARTING`** | Serve pipeline is _initialized_ with inputs \(i.e. source bundle\) |
| **`PIPELINE_RUNNING`** | Serve pipeline _running_ with valid endpoint |
| **`PIPELINE_RESTARTING`** | Serve pipeline is _restarting_ with new inputs |
| **`PIPELINE_FAILURE`** | Serve pipeline _failed_ \(likely due to network or resource problems\) |

