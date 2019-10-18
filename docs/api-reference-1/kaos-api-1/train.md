# /train

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}" %}
{% api-method-summary %}
list training jobs
{% endapi-method-summary %}

{% api-method-description %}
This route lists all **training** jobs within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}/inspect" %}
{% api-method-summary %}
inspect training pipeline
{% endapi-method-summary %}

{% api-method-description %}
This route **inspects** the current training pipeline within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspaces\_\_
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}" %}
{% api-method-summary %}
create training job
{% endapi-method-summary %}

{% api-method-description %}
This route creates a new **training** job within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}

{% api-method-query-parameters %}
{% api-method-parameter name="user" type="string" %}
user for tracking ownership of training job
{% endapi-method-parameter %}
{% endapi-method-query-parameters %}

{% api-method-body-parameters %}
{% api-method-parameter name="data" type="string" required=true %}
binary source bundle
{% endapi-method-parameter %}
{% endapi-method-body-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}/{job\_id}" %}
{% api-method-summary %}
training job info
{% endapi-method-summary %}

{% api-method-description %}
This route returns information about a particular **training** job within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="job\_id" type="string" required=true %}
selected **training** job id
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}

{% api-method-query-parameters %}
{% api-method-parameter name="page\_id" type="integer" required=false %}
page number for pagination of listing itrained models
{% endapi-method-parameter %}

{% api-method-parameter name="sort\_by" type="string" required=false %}
metric for sorting trained models
{% endapi-method-parameter %}
{% endapi-method-query-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}/{job\_id}/bundle" %}
{% api-method-summary %}
source training bundle
{% endapi-method-summary %}

{% api-method-description %}
This route retrieves the source bundle associated with a particular **training** job within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="job\_id" type="string" required=true %}
selected job id \(training\)
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}

{% api-method-query-parameters %}
{% api-method-parameter name="include-code" type="boolean" required=false %}
flag for downloading source code
{% endapi-method-parameter %}

{% api-method-parameter name="include-data" type="boolean" required=false %}
flag for downloading source data
{% endapi-method-parameter %}

{% api-method-parameter name="include-model" type="boolean" required=false %}
flag for downloading trained model
{% endapi-method-parameter %}
{% endapi-method-query-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}/{model\_id}/provenance" %}
{% api-method-summary %}
training model provenance
{% endapi-method-summary %}

{% api-method-description %}
This route retrieves the provenance of a particular trained **model** within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="model\_id" type="string" required=true %}
selected model id
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}/{job\_id}/logs" %}
{% api-method-summary %}
training job logs
{% endapi-method-summary %}

{% api-method-description %}
This route retrieves logs associated with a particular **training** job within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="job\_id" type="string" required=true %}
selected **training** job id
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="delete" host="https://xxxx.yyyy.zzzz.com" path="/train/{workspace}/{job\_id}/" %}
{% api-method-summary %}
kill a training job
{% endapi-method-summary %}

{% api-method-description %}
Allows to kill building and running training jobs
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="job\_id" type="string" required=true %}
selected training or building job id
{% endapi-method-parameter %}

{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}
Is returned if the job was successfully killed
{% endapi-method-response-example-description %}

```

```
{% endapi-method-response-example %}

{% api-method-response-example httpCode=400 %}
{% api-method-response-example-description %}
Is returned if  the job was not in a running state
{% endapi-method-response-example-description %}

```javascript
{"error_code": "JOB_NOT_RUNNING", "message": "Job is not running, id: 1234"}
```
{% endapi-method-response-example %}

{% api-method-response-example httpCode=404 %}
{% api-method-response-example-description %}
Is returned if the job is not found
{% endapi-method-response-example-description %}

```javascript
{"error_code": "JOB_NOT_FOUND", "message": "There is no job with id: 1234"}
```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

