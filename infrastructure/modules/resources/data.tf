
data "external" "resources" {
  program = ["bash", var.script]
}
