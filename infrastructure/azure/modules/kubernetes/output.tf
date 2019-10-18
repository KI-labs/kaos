output "kubeconfig_host" {
  value = azurerm_kubernetes_cluster.this.kube_config[0].host
}

output "kubeconfig_username" {
  value = azurerm_kubernetes_cluster.this.kube_config[0].username
}

output "kubeconfig_password" {
  value = azurerm_kubernetes_cluster.this.kube_config[0].password
}

output "kubeconfig_client_certificate" {
  value = azurerm_kubernetes_cluster.this.kube_config[0].client_certificate
}

output "kubeconfig_client_key" {
  value = azurerm_kubernetes_cluster.this.kube_config[0].client_key
}

output "kubeconfig_cluster_ca_certificate" {
  value = azurerm_kubernetes_cluster.this.kube_config[0].cluster_ca_certificate
}

output "kubeconfig_filename" {
  value = element(concat(local_file.kubeconfig.*.filename, [""]), 0)
}

