variable "tags" {
  type = map(string)
}

variable "aws_access_key_id" {
}

variable "aws_secret_access_key" {
}

# EKS Variables
variable "region" {}

variable "worker_groups_type" {
  default = "cpu_only"
}

variable "cpu_instance_type_aws" {
  default = "m5.large"
}

variable "cpu_min_node_count" {
  default = 1
}

variable "cpu_desired_node_count" {
  default = 3
}

variable "cpu_max_node_count" {
  default = 10
}

variable "cpu_autoscaling_enabled" {
  default = true
}

variable "gpu_instance_type_aws" {
  default = "p2.xlarge"
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

variable "gpu_autoscaling_enabled" {
  default = true
}

variable "main_cidr_block" {
  default = "10.0.0.0/16"
}

variable "private_subnets" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  type    = list(string)
  default = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
}

variable "api_tag" {
  type    = string
  default = "latest"
}

variable "pull_backend_image_policy" {
  default = "Always"
}

variable "pachyderm_tag" {
  type    = string
  default = "1.9.8"
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

variable "token" {
}
