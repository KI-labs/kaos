module "ml_platform" {
  source                    = "../modules/ml_platform"
  backend_uri               = module.docker_build.image_uri[0]
  base_build_uri            = module.docker_build.image_uri[1]
  pachyderm_tag             = var.pachyderm_tag
  pull_backend_image_policy = var.pull_backend_image_policy

  wait_for_ready_state = true
  scripts_dir          = "${path.module}/../../scripts"
  docker_registry      = "LOCAL"
  cpu_counts           = module.resources.cpu_counts
  gpu_counts           = module.resources.gpu_counts
  memory_counts        = module.resources.memory_counts

  # kubernetes service api
  api_memory_request = var.api_memory_request
  api_memory_limit = var.api_memory_limit
  api_cpu_request = var.api_cpu_request
  api_cpu_limit = var.api_cpu_limit
}

module "docker_build" {
  source = "../modules/docker_build"

  image_names = [
    "backend",
    "build-base",
  ]

  image_tags = [
    var.api_tag,
    "latest",
  ]

  docker_contexts = [
    //    "${path.module}/../../backend",
    "${path.module}/../..",
    "${path.module}/../../images/base-build",
  ]

  docker_files = [
    "${path.module}/../../backend/Dockerfile",
    "${path.module}/../../images/base-build/Dockerfile",
  ]

  scripts_dir = "${path.module}/../../scripts"
}

module "output_config" {
  source              = "../modules/output_config"
  backend_domain      = module.ml_platform.backend_domain
  backend_port        = module.ml_platform.backend_port
  kubeconfig_filename = ""
  out_dir             = var.config_dir
  backend_path        = module.ml_platform.backend_path
}


module "resources" {
  source = "../modules/resources"
  script = "${path.module}/../../scripts/local/resources.sh"
}
