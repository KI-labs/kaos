output "network_link" {
  description = "link to network vpn"
  value       = google_compute_network.k8s-network.self_link
}

output "subnetwork_link" {
  description = "link to subnetwork vpn"
  value       = google_compute_subnetwork.k8s-subnetwork.self_link
}

