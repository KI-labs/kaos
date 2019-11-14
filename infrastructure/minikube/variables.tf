variable "api_image" {
  default = "kaos-backend"
}

variable "api_tag" {
  default = "latest"
}

variable "pachyderm_tag" {
  type    = "string"
  default = "1.9.8"
}

variable "pull_backend_image_policy" {
  default = "Never"
}

variable "config_dir" {
  description = "output config json"
  default     = "./"
}

variable "api_memory_request" {
  default = "256Mi"
}

variable "api_memory_limit" {
  default = "512Mi"
}

variable "api_cpu_request" {
  default = "0"
}

variable "api_cpu_limit" {
  default = "1"
}