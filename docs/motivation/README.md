# Motivation

The development of kaos was fueled by our ambition to mimic natural **incremental** model development, simplify model **reproducibility and collaboration**, and automate **ML** **infrastructure** deployment in a **flexible** language-agnostic environment.

## Incremental Development is Natural

The typical Data Science workflow is an **iterative** end-to-end pipeline. It is extremely unlikely that the first inputs result in a final model. Inputs are **always changing** due to additional training data, an improved model architecture, new tuning parameters, etc... The natural problem solving flow is _temporal_ in nature since we adapt to outcomes - i.e. try X, adapt X, try Y, adapt Y, etc...

{% hint style="danger" %}
Typical tooling **ignores** the reality of natural temporal incremental development
{% endhint %}

{% hint style="success" %}
[kaos **mimics** natural incremental model development with dynamic pipelines](incremental-development.md)
{% endhint %}

## Reproducibility is Tricky

Data Scientists rely on sampling from large datasets, building interactive visualizations, performing exhaustive statistical analyses, engineering features, developing models, and evaluating model metrics prior to delivery into production. The process is performed in many **iterations**, which inherently requires tracking which inputs and what processing caused what output \(i.e. data provenance\).

{% hint style="danger" %}
Tracking provenance **explodes** when _multiple_ users share _multiple_ models and their respective inputs \(e.g. code, environment, data, and parameters\).
{% endhint %}

{% hint style="success" %}
[kaos ensures code, environment, data and parameters are **reproducible with full provenance**](reproducibility.md)\*\*\*\*
{% endhint %}

## ML Infrastructure is Tough

Data Scientists use multiple technologies and tools for data processing, algorithm and model development. This mandates the knowledge of what underlying resources are necessary for each task.

{% hint style="danger" %}
Deploying **stable** elastic infrastructure requires detailed knowledge of authentication, processing, storage and networking \(i.e. DevOps\).
{% endhint %}

{% hint style="success" %}
[kaos **automates infrastructure deployment** with Infrastructure as Code](infrastructure-automation.md)
{% endhint %}

## Flexibility Flexibility Flexibility

Data Scientists require diverse libraries for processing features and/or training models, which is typically linked to a preferred programming language. Tooling flexibility is an absolute necessity to ensure Data Scientists are not hindered throughout their workflow.

{% hint style="danger" %}
A flexible tool **must** handle different frameworks, packages and languages.
{% endhint %}

{% hint style="success" %}
[kaos core is built with **language agnostic data pipelines** supporting any framework](flexibility.md)
{% endhint %}

