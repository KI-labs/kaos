# Workspaces

Workspaces are a similar concept to [kubernetes namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) since their main intention is to provide and shared environment across multiple users \(or teams\). Unlike kubernetes, kaos absolutely requires a workspace for all work. A workspace is ideally an environment for training a single "type" of model - for example `mnist`.

{% hint style="warning" %}
**A workspace consists of only a single dynamic train pipeline** - a requirement to have full provenance while incrementally developing machine learning models.
{% endhint %}

Workspaces can be shared by connecting to an existing workspace via `kaos workspace set` assuming the workspace has been first created \(i.e. `kaos workspace create`\).

{% hint style="info" %}
It is **not necessary** to use multiple workspaces for a slightly different model!
{% endhint %}

