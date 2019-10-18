//config
variable "gcp_project_name" {
}

variable "project_location" {
}

variable "project_region" {
  default = "eu"
}

variable "backend_name" {
  type    = string
  default = "kaos-backend"
}

variable "backend_tag" {
  type    = string
  default = "latest"
}

//kubernetes
variable "horizontal_pod_autoscaling" {
  default = "false"
}

variable "http_load_balancing" {
  default = "false"
}

variable "kubernetes_dashboard" {
  default = "false"
}

variable "network_policy_config" {
  default = "false"
}

variable "enable_kubernetes_alpha" {
  default = "false"
}

variable "enable_legacy_abac" {
  default = "false"
}

variable "maintenance_start_time" {
  default = "03:00"
}

variable "description" {
}

variable "disk_size_gb" {
}

variable "disk_type" {
}

variable "oauth_scopes" {
  type = list(string)
  default = [
    "https://www.googleapis.com/auth/logging.write",
    "https://www.googleapis.com/auth/monitoring",
    "https://www.googleapis.com/auth/devstorage.read_write",
  ]
}

variable "preemptible" {
}

variable "service_account" {
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "node_tags" {
  type    = list(string)
  default = []
}

variable "metadata" {
  type = map(string)
  default = {
    disable-legacy-endpoints = true
  }

}

variable "auto_repair" {
  default = true
}

variable "auto_upgrade" {
  default = false
}

variable "base_build_tag" {
  type    = string
  default = "latest"
}

//networking
variable "subnetwork_name" {
}

variable "ip_cidr_range" {
}

variable "secondary_range_name" {
}

variable "secondary_ip_cidr_range" {
}

variable "network_name" {
}

variable "auto_create_subnetworks" {
  default = false
}

//storage
variable "bucket_name" {
}

//ml-platform
variable "pull_backend_image_policy" {
  default = "Always"
}

variable "pachyderm_tag" {
}

//output_config

variable "config_dir" {
  description = "output config json"
  default     = "./"
}

//other
variable "tags" {
  type = map(string)
}

variable "worker_groups_type" {
  default = "cpu_only"
}

variable "cpu_instance_type_gcp" {
  default = "n1-standard-2"
}

variable "cpu_min_node_count" {
  default = 1
}

variable "cpu_desired_node_count" {
  default = 2
}

variable "cpu_max_node_count" {
  default = 5
}

variable "gpu_instance_type_gcp" {
  default = "n1-standard-4"
}

variable "gpu_accelerator_type" {
  default = "nvidia-tesla-p100"
}

variable "gpu_min_node_count" {
  default = 0
}

variable "gpu_desired_node_count" {
  default = 1
}

variable "gpu_max_node_count" {
  default = 1
}

variable "gpu_accelerator_count" {
  default = 1
}

variable "credentials_path" {
}

variable "api_memory_request" {
  default = "1Gi"
}

variable "api_memory_limit" {
  default = "2Gi"
}

variable "api_cpu_request" {
  default = "0.5"
}

variable "api_cpu_limit" {
  default = "1.5"
}
