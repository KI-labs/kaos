# /internal

{% api-method method="delete" host="https://xxxx.yyyy.zzzz.com" path="/internal/resources" %}

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/internal/train\_pipeline/{workspace}/{user}" %}
{% api-method-summary %}

{% endapi-method-summary %}

{% api-method-description %}
This route **creates \(or updates\) a training pipeline** within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="user" type="string" required=true %}
user for tracking ownership of training
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}

{% api-method-query-parameters %}
{% api-method-parameter name="registry" type="string" required=false %}
docker registry containing &lt;image\_name&gt;
{% endapi-method-parameter %}

{% api-method-parameter name="image\_name" type="string" %}
name of image for running training
{% endapi-method-parameter %}
{% endapi-method-query-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```text

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/internal/notebook\_pipeline/{workspace}/{user}" %}
{% api-method-summary %}
create notebook pipeline
{% endapi-method-summary %}

{% api-method-description %}
This route **creates \(or updates\) a notebook pipeline** within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="user" type="string" required=true %}
user for tracking ownership of notebook
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}

{% api-method-query-parameters %}
{% api-method-parameter name="registry" type="string" required=false %}
docker registry containing &lt;image\_name&gt;
{% endapi-method-parameter %}

{% api-method-parameter name="image\_name" type="string" %}
name of image for spawning notebook
{% endapi-method-parameter %}
{% endapi-method-query-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```text

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

{% api-method method="post" host="https://xxxx.yyyy.zzzz.com" path="/internal/serve\_pipeline/{workspace}/{user}" %}
{% api-method-summary %}
create serve pipeline
{% endapi-method-summary %}

{% api-method-description %}
This route **creates \(or updates\) a serve pipeline** within a workspace.
{% endapi-method-description %}

{% api-method-spec %}
{% api-method-request %}
{% api-method-path-parameters %}
{% api-method-parameter name="workspace" type="string" required=true %}
selected workspace
{% endapi-method-parameter %}

{% api-method-parameter name="user" type="string" required=true %}
user for tracking ownership of notebook
{% endapi-method-parameter %}
{% endapi-method-path-parameters %}

{% api-method-query-parameters %}
{% api-method-parameter name="registry" type="string" required=false %}
docker registry containing &lt;image\_name&gt;
{% endapi-method-parameter %}

{% api-method-parameter name="image\_name" type="string" %}
name of image for spawning notebook
{% endapi-method-parameter %}
{% endapi-method-query-parameters %}
{% endapi-method-request %}

{% api-method-response %}
{% api-method-response-example httpCode=200 %}
{% api-method-response-example-description %}

{% endapi-method-response-example-description %}

```text

```
{% endapi-method-response-example %}
{% endapi-method-response %}
{% endapi-method-spec %}
{% endapi-method %}

