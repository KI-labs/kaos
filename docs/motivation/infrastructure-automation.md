# ✔ Infrastructure Automation

All underlying kaos infrastructure is deployed with code - known as Infrastructure as Code \(IaC\). Infrastructure as Code is extremely beneficial since it is somewhat self-service, meaning DevOps knowledge is democratised and avoids bottlenecks as the platform grows. The main benefits of deploying infrastructure with code are listed below.

* **Speed and Simplicity**
  * Deploy an entire infrastructure by running code
* **Consistency**
  * Avoid human error with standardization
* **Immediate Documentation**
  * Code overview detailing all components
* **Cost Effective**
  * Avoid wasting time on manual tasks
* **Version Control**
  * Save snapshots of infrastructure with VCS

{% hint style="success" %}
kaos immediately provides **all benefits** of automated infrastructure deployment
{% endhint %}

The kaos backend infrastructure contains **all necessary components** for an ML platform - persistent storage, private networking, private Docker registry, and an elastic kubernetes cluster. kaos also supports **multiple environments**, including development, staging, and production.

kaos currently supports the following environments \(both local and cloud\).

* **Local**
  * [Docker Desktop](../getting-started/deploying-infrastructure/#docker-desktop)
* **Cloud**
  * [Amazon Web Services \(**AWS**\)](../getting-started/deploying-infrastructure/#amazon-web-services-aws)
  * [Google Cloud Platform \(**GCP**\)](../getting-started/deploying-infrastructure/#google-cloud-platform-gcp)
  * [Microsoft Azure \(**AZ**\)](../getting-started/deploying-infrastructure/#microsoft-azure-az)

