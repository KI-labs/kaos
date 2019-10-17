variable "scripts_dir" {}

variable "docker_contexts" {
  type = "list"
}

variable "docker_files" {
  type = "list"
}

variable "image_tags" {
  type = "list"
}

variable "image_names" {
  type = "list"
}

variable "is_minikube" {
  default = false
}
