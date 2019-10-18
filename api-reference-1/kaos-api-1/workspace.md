# /workspace

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/workspace" %}
{% api-method-summary %}
list workspace
{% endapi-method-summary %}

{% api-method-description %}
This route lists all existing **workspaces** within kaos
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="" type="string" required=false %}

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

{% api-method method="get" host="https://xxxx.yyyy.zzzz.com" path="/workspace/{workspace}" %}
{% api-method-summary %}
workspace info
{% endapi-method-summary %}

{% api-method-description %}
This route describes an existing **workspace** within kaos.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-query-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
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

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/workspace/{workspace}" %}
{% api-method-summary %}
create workspace
{% endapi-method-summary %}

{% api-method-description %}
This route creates a new **workspace** within kaos.
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
user for tracking ownership of parameters
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

{% api-method method="delete" host="https://xxxx.yyyy.zzzz.com" path="/workspace/{workspace}" %}
{% api-method-summary %}
remove workspace
{% endapi-method-summary %}

{% api-method-description %}
This route removes an existing **workspace** within kaos.
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

