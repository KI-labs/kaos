//config
project_location = "europe-west4-a"

gcp_project_name = "kaos-236414"

tags = {
  project_name = "kaos"
  version      = "2"
  env          = "prod"
}

//kubernetes
description = "Kaos Cluster"

disk_size_gb = 200

disk_type = "pd-standard"

preemptible = "true"

service_account = "kaos-kubernetes@kaos-236414.iam.gserviceaccount.com"

//networking
subnetwork_name = "vnet-k8s-subnetwork"

ip_cidr_range = "10.2.0.0/16"

secondary_range_name = "vnet-k8s-subnetwork-secondary-range"

secondary_ip_cidr_range = "192.168.2.0/24"

network_name = "vnet"

//storage
bucket_name = "store"

//ml-platform
pachyderm_tag = "1.9.8"

worker_groups_type = "cpu_only"
