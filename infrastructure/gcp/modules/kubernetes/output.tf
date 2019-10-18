output "cluster_endpoint" {
  description = "address of kubernetes cluster"
  value       = google_container_cluster.new_container_cluster.endpoint
}

output "cluster_ca_certificate" {
  description = "address of kubernetes cluster"
  value       = google_container_cluster.new_container_cluster.master_auth[0].cluster_ca_certificate
}

output "kubeconfig_filename" {
  value = local_file.kubeconfig.filename
}

