# ✔ Incremental Development

The natural **iterative** and **incremental** problem solving approach of forming, testing and validating hypotheses is present in kaos. Machine learning is similar to any problem with unknown dimensionality, which requires continual improvement towards a desired end goal \(i.e. a specific metric or desired KPI\).

kaos simulates this process by allowing **any number of** **training inputs** - code, data and/or params. A simplified conceptual example is presented below.

{% tabs %}
{% tab title="Time₀" %}
| Inputs | kaos Command |
| :--- | :--- |
| Code, Data, Params | `kaos train deploy -s <code> -d <data>` |

{% hint style="danger" %}
Resulting model trained with **incorrect architecture**
{% endhint %}
{% endtab %}

{% tab title="Time₁" %}
| Inputs | kaos Command |
| :--- | :--- |
| Code with **correct** architecture | `kaos train deploy -s <code>` |

{% hint style="danger" %}
Resulting model trained with **poorly labelled training dataset**
{% endhint %}
{% endtab %}

{% tab title="Time₂" %}
| Inputs | kaos Command |
| :--- | :--- |
| Data with **relabelled** training data | `kaos train deploy -d <data>` |

{% hint style="danger" %}
Resulting model trained with **assumed learning rate**
{% endhint %}
{% endtab %}

{% tab title="Timeₙ" %}
| Inputs | kaos Commands |
| :--- | :--- |
| Hyperparameters with **range** of learning rates | `kaos train deploy -h <hyperparams>` |

{% hint style="success" %}
Resulting model **satisfies** the desired KPI!
{% endhint %}
{% endtab %}
{% endtabs %}

![incremental model development in time with kaos](../.gitbook/assets/image-26.png)

{% hint style="success" %}
kaos enables incremental processing when **any or all updated inputs are desired**
{% endhint %}

Check out the [Training Pipeline](../usage/high-level-usage/ml-deployment/train-pipeline.md) for detailed information regarding its inputs and outputs.

