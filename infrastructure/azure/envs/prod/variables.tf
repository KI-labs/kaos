variable "tags" {
  type = map(string)
}

variable "k8s_subnet_cidr" {
}

variable "k8s_vm_size" {
}

variable "os_disk_size_in_gb" {
}

variable "worker_node_count" {
}

variable "k8s_network_cidr" {
}

variable "SERVICE_PRINCIPAL_ID" {
}

variable "SERVICE_PRINCIPAL_SECRET" {
}

variable "SUBSCRIPTION_ID" {
}

variable "CLIENT_ID" {
}

variable "CLIENT_SECRET" {
}

variable "TENANT_ID" {
}

## Storgae Variables

variable "storage_rg_specs" {
  type = map(string)
}

variable "storage_account_name" {
}

## Networking Variables
variable "network_rg_specs" {
  type = map(string)
}

variable "subnet_address_space" {
}

variable "network_address_space" {
}

variable "subnet_count" {
}

variable "api_tag" {
  type    = string
  default = "latest"
}

variable "region" {
  default = "westeurope"
}

variable "pachyderm_tag" {
  default = "1.9.8"
}

variable "pull_backend_image_policy" {
  default = "Always"
}

variable "registry_email" {
}

variable "admin_username" {
}

variable "config_dir" {
  description = "output config json"
  default     = "./"
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

