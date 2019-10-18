data "local_file" "ssh_pub_key" {
  filename = pathexpand("~/.ssh/id_rsa.pub")
}

resource "local_file" "kubeconfig" {
  content  = azurerm_kubernetes_cluster.this.kube_config_raw
  filename = "${var.config_output_path}kubeconfig_${var.kubeconfig_name}"
  count    = var.write_kubeconfig ? 1 : 0
}

