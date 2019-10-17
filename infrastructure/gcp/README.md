# Google Cloud Platform (GCP)

### Requirements
 - (service) account on GCP with following roles:
    * Compute Network Admin
    * Kubernetes Engine Admin
    * Kubernetes Engine Cluster Admin
    * Kubernetes Engine Developer
    * Role Viewer
    * Security Reviewer
    * Create Service Accounts
    * Service Account User
    * Storage Admin
    * Storage Object Admin

### Environment Variables
The following env variables must be exported

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credential.json"
export KAOS_HOME=/path/to/kaos/source/code/root/
# Optional
export TF_VAR_min_node_count=# (default: 1)
export TF_VAR_max_node_count=# (default: 10)
export TF_VAR_desired_node_count=# (default: 2)
export TF_VAR_instance_type=####### (defaul: n1-standard-1)

```

### Tests
First install `inspec`: https://github.com/inspec/inspec

To run tests go to `infrastructure/gcp/test/integration` and run:
```bash
inspec exec . -t gcp:// --input-file attributes.yml 
```
