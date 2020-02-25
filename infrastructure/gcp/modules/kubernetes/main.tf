resource "google_container_cluster" "new_container_cluster" {
  name                     = var.cluster_name
  description              = var.description
  location                 = var.cluster_location
  network                  = var.network
  subnetwork               = var.subnetwork
  initial_node_count       = var.cpu_node_count
  remove_default_node_pool = true

  addons_config {
    horizontal_pod_autoscaling {
      disabled = var.horizontal_pod_autoscaling
    }

    http_load_balancing {
      disabled = var.http_load_balancing
    }

//    kubernetes_dashboard {
//      disabled = var.kubernetes_dashboard
//    }
    //    network_policy_config {
    //      disabled = "${var.network_policy_config}"
    //    }
  }

  # cluster_ipv4_cidr - default
  enable_kubernetes_alpha = var.enable_kubernetes_alpha
  enable_legacy_abac      = var.enable_legacy_abac

  maintenance_policy {
    daily_maintenance_window {
      start_time = var.maintenance_start_time
    }
  }

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }

    username = ""
    password = ""
  }
}

resource "google_container_node_pool" "cpu_node_pool" {
  name       = var.cpu_pool_name
  location   = var.cluster_location
  node_count = var.cpu_node_count
  cluster    = google_container_cluster.new_container_cluster.name

  node_config {
    disk_size_gb = var.disk_size_gb
    disk_type    = var.disk_type
    machine_type = var.cpu_machine_type

    oauth_scopes    = var.oauth_scopes
    preemptible     = var.preemptible
    service_account = var.service_account
    labels          = var.labels
    tags            = var.node_tags
    metadata        = var.metadata
  }

  autoscaling {
    min_node_count = var.cpu_min_node_count
    max_node_count = var.cpu_max_node_count
  }

  management {
    auto_repair  = var.auto_repair
    auto_upgrade = var.auto_upgrade
  }
}


resource "google_container_node_pool" "gpu_node_pool" {
  count      = var.worker_groups_type == "cpu_gpu" ? 1 : 0
  name       = var.gpu_pool_name
  location   = var.cluster_location
  node_count = var.gpu_node_count
  cluster    = google_container_cluster.new_container_cluster.name

  node_config {
    disk_size_gb = var.disk_size_gb
    disk_type    = var.disk_type
    machine_type = var.gpu_machine_type

    oauth_scopes    = var.oauth_scopes
    preemptible     = var.preemptible
    service_account = var.service_account
    labels          = var.labels
    tags            = var.node_tags
    metadata        = var.metadata
    guest_accelerator = [
      {
        type  = var.gpu_accelerator_type
        count = var.gpu_accelerator_count
      },
    ]
  }

  autoscaling {
    min_node_count = var.gpu_min_node_count
    max_node_count = var.gpu_max_node_count
  }

  management {
    auto_repair  = var.auto_repair
    auto_upgrade = var.auto_upgrade
  }
}

data "template_file" "kubeconfig" {
  template = file("${path.module}/template-kubeconfig.yaml")

  vars = {
    kubeconfig_name = var.cluster_name
    cluster_name    = google_container_cluster.new_container_cluster.name
    endpoint        = google_container_cluster.new_container_cluster.endpoint
    cluster_ca      = google_container_cluster.new_container_cluster.master_auth[0].cluster_ca_certificate
    access_token    = var.access_token
  }
}

resource "local_file" "kubeconfig" {
  content  = data.template_file.kubeconfig.rendered
  filename = "${var.config_output_path}/${var.kubeconfig_name}"
}

