locals {
  prefix = "${var.tags["project_name"]}-${var.tags["version"]}-${terraform.workspace}"
}
