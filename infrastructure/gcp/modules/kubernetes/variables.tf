variable "network" {
}

variable "subnetwork" {
}

variable "cluster_name" {
}

variable "cluster_location" {
}

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

variable "kubeconfig_name" {
}

variable "config_output_path" {
}

variable "cpu_pool_name" {
}

variable "gpu_pool_name" {
}

variable "pool_location" {
}

variable "disk_size_gb" {
}

variable "disk_type" {
}

variable "oauth_scopes" {
  type = list(string)
}

variable "preemptible" {
}

variable "service_account" {
}

variable "labels" {
  type = map(string)
}

variable "node_tags" {
  type = list(string)
}

variable "metadata" {
  type = map(string)
}

variable "auto_repair" {
}

variable "auto_upgrade" {
}

variable "tags" {
  type = map(string)
}

variable "access_token" {

}
variable "cpu_node_count" {

}
variable "cpu_min_node_count" {

}
variable "cpu_max_node_count" {

}
variable "cpu_machine_type" {

}
variable "gpu_node_count" {

}
variable "gpu_min_node_count" {

}
variable "gpu_max_node_count" {

}
variable "gpu_machine_type" {

}
variable "gpu_accelerator_type" {

}

variable "gpu_accelerator_count" {

}

variable "worker_groups_type" {

}