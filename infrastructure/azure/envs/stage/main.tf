locals {
  prefix = "${var.tags["project"]}-${var.tags["version"]}-${terraform.workspace}"
}

module "kubernetes" {
  source                   = "../../modules/kubernetes"
  prefix                   = local.prefix
  k8s_network_cidr         = var.k8s_network_cidr
  k8s_subnet_cidr          = var.k8s_subnet_cidr
  k8s_vm_size              = var.k8s_vm_size
  os_disk_size_in_gb       = var.os_disk_size_in_gb
  worker_node_count        = var.worker_node_count
  service_principal_id     = var.SERVICE_PRINCIPAL_ID
  kubeconfig_name          = local.prefix
  config_output_path       = "${path.module}/"
  service_principal_secret = var.SERVICE_PRINCIPAL_SECRET
  acr_registry_id          = module.registry.registry_id
  admin_username           = var.admin_username
  tags                     = var.tags
}

module "storage" {
  source               = "../../modules/storage"
  prefix               = local.prefix
  storage_account_name = var.storage_account_name
  storage_rg_specs     = var.storage_rg_specs
  tags                 = var.tags
}

module "networking" {
  source                = "../../modules/networking"
  prefix                = local.prefix
  network_rg_specs      = var.network_rg_specs
  subnet_address_space  = var.subnet_address_space
  network_address_space = var.network_address_space
  subnet_count          = var.subnet_count
  tags                  = var.tags
}

module "registry" {
  source = "../../modules/registry"

  image_names = [
    "${var.tags["project"]}backend",
    "${var.tags["project"]}build",
  ]

  image_tags = [
    var.api_tag,
    "latest",
  ]

  docker_contexts = [
    //    "${path.module}/../../../../backend",
    "${path.module}/../../../..", # FIXME!!!!
    "${path.module}/../../../../images/base-build",
  ]

  docker_files = [
    "${path.module}/../../../../backend/Dockerfile",
    "${path.module}/../../../../images/base-build/Dockerfile",
  ]

  region               = var.region
  scripts_dir          = "${path.module}/../../../../scripts"
  prefix               = local.prefix
  storage_account_name = module.storage.storage_account_name
  tags                 = var.tags
}

module "ml_platform" {
  source                    = "../../../modules/ml_platform"
  backend_uri               = module.registry.image_uri[0]
  base_build_uri            = module.registry.image_uri[1]
  pull_backend_image_policy = var.pull_backend_image_policy
  pachyderm_tag             = var.pachyderm_tag
  storage_backend           = "MICROSOFT"
  ingress_type              = "NodePort"

  # kubernetes service api
  api_memory_request = var.api_memory_request
  api_memory_limit = var.api_memory_limit
  api_cpu_request = var.api_cpu_request
  api_cpu_limit = var.api_cpu_limit

  docker_registry = module.registry.registry_name
  docker_username = module.registry.registry_username
  docker_password = module.registry.registry_password
  docker_email    = var.registry_email

  data = {
    microsoft-container = module.storage.storage_container_name
    microsoft-id        = module.storage.storage_account_name
    microsoft-secret    = module.storage.storage_access_key
  }

  kubeconfig_filename = module.kubernetes.kubeconfig_filename
  scripts_dir         = "${path.module}/../../../../scripts"
  nodes               = var.worker_node_count
}

module "output_config" {
  source              = "../../../modules/output_config"
  backend_domain      = module.ml_platform.backend_domain
  backend_port        = module.ml_platform.backend_port
  kubeconfig_filename = module.kubernetes.kubeconfig_filename
  out_dir             = var.config_dir
  backend_path        = module.ml_platform.backend_path
}
