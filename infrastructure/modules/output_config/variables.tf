variable "kubeconfig_filename" {
  default = ""
}

variable "out_dir" {
  description = "output directory"
  default     = "./"
}

variable "backend_port" {}

variable "backend_domain" {
  type = "list"
}

variable "backend_path" {}
