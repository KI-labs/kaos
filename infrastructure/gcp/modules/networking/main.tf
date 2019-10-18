resource "google_compute_subnetwork" "k8s-subnetwork" {
  name          = var.subnetwork_name
  ip_cidr_range = var.ip_cidr_range
  region        = "europe-west4"
  network       = var.network_name

  secondary_ip_range {
    range_name    = var.secondary_range_name
    ip_cidr_range = var.secondary_ip_cidr_range
  }

  depends_on = [google_compute_network.k8s-network]
}

resource "google_compute_network" "k8s-network" {
  name                    = var.network_name
  auto_create_subnetworks = var.auto_create_subnetworks
}

