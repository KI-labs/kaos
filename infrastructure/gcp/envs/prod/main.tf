module "kubernetes" {
  source                     = "../../modules/kubernetes"
  network                    = module.networking.network_link
  subnetwork                 = module.networking.subnetwork_link
  node_tags                  = var.node_tags
  cluster_name               = local.prefix
  cluster_location           = var.project_location
  cpu_node_count             = var.cpu_desired_node_count
  cpu_min_node_count         = var.cpu_min_node_count
  cpu_max_node_count         = var.cpu_max_node_count
  cpu_machine_type           = var.cpu_instance_type_gcp
  gpu_node_count             = var.gpu_desired_node_count
  gpu_min_node_count         = var.gpu_min_node_count
  gpu_max_node_count         = var.gpu_max_node_count
  gpu_machine_type           = var.gpu_instance_type_gcp
  gpu_accelerator_type       = var.gpu_accelerator_type
  gpu_accelerator_count      = var.gpu_accelerator_count
  worker_groups_type         = var.worker_groups_type
  cpu_pool_name              = local.prefix
  gpu_pool_name              = "gpu-${local.prefix}"
  pool_location              = var.project_location
  disk_size_gb               = var.disk_size_gb
  disk_type                  = var.disk_type
  oauth_scopes               = var.oauth_scopes
  preemptible                = var.preemptible
  service_account            = var.service_account
  labels                     = var.labels
  metadata                   = var.metadata
  auto_repair                = var.auto_repair
  auto_upgrade               = var.auto_upgrade
  horizontal_pod_autoscaling = var.horizontal_pod_autoscaling
  http_load_balancing        = var.http_load_balancing
  kubernetes_dashboard       = var.kubernetes_dashboard
  network_policy_config      = var.network_policy_config
  enable_kubernetes_alpha    = var.enable_kubernetes_alpha
  enable_legacy_abac         = var.enable_legacy_abac
  kubeconfig_name            = "kubeconfig"
  config_output_path         = path.module
  maintenance_start_time     = var.maintenance_start_time
  description                = var.description
  access_token               = data.google_client_config.current.access_token
  tags                       = var.tags
}

module "storage" {
  source          = "../../modules/storage"
  bucket_name     = "${local.prefix}-${var.bucket_name}"
  bucket_location = upper(var.project_region)
  tags            = var.tags
}

module "networking" {
  source                  = "../../modules/networking"
  subnetwork_name         = "${local.prefix}-${var.subnetwork_name}"
  ip_cidr_range           = var.ip_cidr_range
  region                  = var.project_location
  secondary_range_name    = "${local.prefix}-${var.secondary_range_name}"
  secondary_ip_cidr_range = var.secondary_ip_cidr_range
  network_name            = "${local.prefix}-${var.network_name}"
  auto_create_subnetworks = var.auto_create_subnetworks
  tags                    = var.tags
}

module "repository" {
  source       = "../../modules/repository"
  project_name = var.gcp_project_name

  image_tags = [
    var.backend_tag,
    "latest",
  ]

  scripts_dir = "${path.module}/../../../../scripts"

  image_names = [
    "${local.prefix}-backend",
    "${local.prefix}-base-build",
  ]

  docker_contexts = [
    "${path.module}/../../../..", # FIXME!!!!
    "${path.module}/../../../../images/base-build",
  ]

  docker_files = [
    "${path.module}/../../../../backend/Dockerfile",
    "${path.module}/../../../../images/base-build/Dockerfile",
  ]

  credentials_path = var.credentials_path
  region           = var.project_region
}


module "workers" {
  source                 = "../../modules/workers"
  worker_groups_type     = var.worker_groups_type
  cpu_desired_node_count = var.cpu_desired_node_count
  cpu_instance_type      = var.cpu_instance_type_gcp
  gpu_desired_node_count = var.gpu_desired_node_count
  gpu_accelerator_count  = var.gpu_accelerator_count
  gpu_instance_type      = var.gpu_instance_type_gcp
  project_location       = var.project_location
}

module "ml_platform" {
  source          = "../../../modules/ml_platform"
  backend_uri     = "${element(module.repository.gcr_location, 0)}:${var.backend_tag}"
  base_build_uri  = "${element(module.repository.gcr_location, 1)}:latest"
  region          = upper(var.project_region)
  docker_registry = module.repository.google_cloud_registry_id
  gpu_counts      = module.workers.gpu_counts
  cpu_counts      = module.workers.cpu_counts
  memory_counts   = module.workers.memory_counts

  # kubernetes service api
  api_memory_request = var.api_memory_request
  api_memory_limit = var.api_memory_limit
  api_cpu_request = var.api_cpu_request
  api_cpu_limit = var.api_cpu_limit

  #add tag
  pull_backend_image_policy = var.pull_backend_image_policy
  pachyderm_tag             = var.pachyderm_tag
  storage_backend           = "GOOGLE"

  token = var.token

  data = {
    google-bucket = module.storage.storage_name
    google-cred   = file(var.credentials_path)
  }

  wait_for_ready_state = true
  scripts_dir          = "${path.module}/../../../../scripts"
  kubeconfig_filename  = module.kubernetes.kubeconfig_filename
  nodes                = module.workers.nodes
  timeout              = 1440
}

module "output_config" {
  source              = "../../../modules/output_config"
  backend_domain      = module.ml_platform.backend_domain
  backend_port        = module.ml_platform.backend_port
  kubeconfig_filename = module.kubernetes.kubeconfig_filename
  out_dir             = var.config_dir
  backend_path        = module.ml_platform.backend_path
}

