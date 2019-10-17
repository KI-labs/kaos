variable "tags" {
  type = map(string)
}

variable "prefix" {
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

variable "service_principal_id" {
}

variable "service_principal_secret" {
}

variable "kubeconfig_name" {
}

variable "acr_registry_id" {
}

variable "admin_username" {
}

variable "config_output_path" {
  default = "./"
}

variable "write_kubeconfig" {
  default = true
}

