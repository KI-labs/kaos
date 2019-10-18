variable "scripts_dir" {
}

variable "docker_contexts" {
  type = list(string)
}

variable "docker_files" {
  type = list(string)
}

variable "image_tags" {
  type = list(string)
}

variable "image_names" {
  type = list(string)
}

variable "region" {
}

