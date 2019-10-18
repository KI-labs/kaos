resource "local_file" "output_config" {
  content  = data.template_file.output_config.rendered
  filename = "${var.out_dir}/config.json"
}

data "template_file" "output_config" {
  template = file("${path.module}/config.json.tpl")

  vars = {
    kubeconfig     = var.kubeconfig_filename
    backend_domain = jsonencode(var.backend_domain)
    backend_port   = var.backend_port
    backend_path   = var.backend_path
  }
}
