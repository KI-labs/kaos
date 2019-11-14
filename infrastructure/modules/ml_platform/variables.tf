variable "backend_uri" {
  type = string
}

variable "pachyderm_tag" {
  type    = string
  default = "1.9.8"
}

variable "pull_backend_image_policy" {
  default = "Never"
}

variable "data" {
  type    = map(string)
  default = {}
}

variable "fake_data" {
  type = map(string)

  default = {
    amazon-id           = "fake_amazon_id"
    amazon-secret       = "fake_amazon_secret"
    amazon-region       = "fake_amazon_region"
    amazon-bucket       = "fake_amazon_bucket"
    google-cred         = "fake-google-cred"
    google-bucket       = "fake-google-bucket"
    microsoft-id        = "fake_microsoft_id"
    microsoft-secret    = "fake_microsoft_secret"
    microsoft-container = "fake_microsoft_container"
  }
}

variable "storage_backend" {
  type        = string
  description = "Pachyderm storage backend"
  default     = "LOCAL"
}

variable "cluster_name" {
  default = "aws_required"
}

variable "cloud_provider" {
  type = map(string)

  default = {
    "LOCAL"     = "LOCAL"
    "AMAZON"    = "AWS"
    "MICROSOFT" = "AZ"
    "GOOGLE"    = "GCP"
  }
}

variable "region" {
  type    = string
  default = "default"
}

variable "docker_registry" {
  type = string
}

variable "docker_username" {
  default = "fake_username"
}

variable "docker_password" {
  default = "fake_password"
}

variable "docker_email" {
  default = "fake_email"
}

variable "ingress_type" {
  default = "LoadBalancer"
}

variable "base_build_uri" {
  default = ""
}

variable "wait_for_ready_state" {
  description = "whether to wait for the cluster to be in ready state before deploying applications"
  default     = false
}

variable "scripts_dir" {
  description = "the script directory"
  default     = ""
}

variable "kubeconfig_filename" {
  description = "the kubeconfig filename"
  default     = ""
}

variable "timeout" {
  description = "the timeout file"
  default     = 360
}

variable "interval" {
  default = 10
}

variable "nodes" {
  default = 1
}

variable "ambassador_service_type" {
  type    = string
  default = "LoadBalancer"
}

variable "ambassador_admin_service_type" {
  type    = string
  default = "NodePort"
}

variable "gpu_counts" {
  type    = "list"
  default = [0]
}

variable "cpu_counts" {
  type    = "list"
  default = [0]
}

variable "memory_counts" {
  type    = "list"
  default = [0]
}

variable "api_memory_request" {
}

variable "api_memory_limit" {
}

variable "api_cpu_request" {
}

variable "api_cpu_limit" {
}


