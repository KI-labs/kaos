# /inference

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/inference/{workspace}" %}
{% api-method-summary %}
list endpoints
{% endapi-method-summary %}

{% api-method-description %}
This route lists all running **endpoints** within a workspace.
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

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/inference/{workspace}/{model\_id}" %}
{% api-method-summary %}
deploy endpoint
{% endapi-method-summary %}

{% api-method-description %}
This route creates a new **endpoint** with a previously trained model within a workspace.
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

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/inference/{workspace}/{endpoint\_name}/bundle" %}
{% api-method-summary %}
source endpoint bundle
{% endapi-method-summary %}

{% api-method-description %}
This route retrieves the **source** bundle associated with a particular training job within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="endpoint\_name" type="string" required=true %}
selected endpoint name
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

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/inference/{workspace}/{endpoint\_name}/provenance" %}
{% api-method-summary %}
endpoint provenance
{% endapi-method-summary %}

{% api-method-description %}
This route retrieves the provenance of a particular **endpoint** within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="endpoint\_name" type="string" required=true %}
selected endpoint name
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

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/inference/{endpoint\_name}/logs" %}
{% api-method-summary %}
endpoint logs
{% endapi-method-summary %}

{% api-method-description %}
This route retrieves logs associated with a particular **endpoint**.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="endpoint\_name" type="string" required=true %}
selected endpoint name
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

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/inference/{workspace}/build/{job\_id}/logs" %}
{% api-method-summary %}
endpoint build logs
{% endapi-method-summary %}

{% api-method-description %}
This route retrieves logs associated with **building** the source endpoint ****image.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="job\_id" type="string" required=true %}
selected **building** job\_id
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

{% api-method method="delete" host="https://xxxx.yyyy.zzzz.com" path="/endpoint/{endpoint\_name}" %}
{% api-method-summary %}
remove endpoint
{% endapi-method-summary %}

{% api-method-description %}
This route removes a running **endpoint** within kaos.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="endpoint\_name" type="string" required=true %}
selected endpoint name
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

