# /notebook

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/notebook/{workspace}" %}
{% api-method-summary %}
list notebooks
{% endapi-method-summary %}

{% api-method-description %}
This route lists all running **notebooks** within kaos.
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

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/notebook/{workspace}" %}
{% api-method-summary %}
create notebooks
{% endapi-method-summary %}

{% api-method-description %}
This route creates a new **notebook** instance.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}

{% api-method-query-parameters %}
{% api-method-parameter name="user" type="string" required=false %}
user for tracking ownership of notebook
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

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/notebook/{workspace}/build/{job\_id}/logs" %}
{% api-method-summary %}
get build logs
{% endapi-method-summary %}

{% api-method-description %}
This route provides access to **logs** from building the source notebook image.
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

{% api-method method="delete" host="https://xxxx.yyyy.zzzz.com" path="/notebook/{notebook\_name}" %}
{% api-method-summary %}
remove notebook
{% endapi-method-summary %}

{% api-method-description %}
This route deletes a running **notebook** instance.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="notebook\_name" type="string" required=true %}
selected notebook name
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



