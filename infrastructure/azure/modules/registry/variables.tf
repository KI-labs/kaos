variable "tags" {
  type = map(string)
}

variable "region" {
}

variable "prefix" {
}

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

variable "storage_account_name" {
}

