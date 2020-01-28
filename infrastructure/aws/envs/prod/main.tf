module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${local.prefix}-vpc"
  cidr = var.main_cidr_block

  azs = [
    data.aws_availability_zones.available.names[0],
    data.aws_availability_zones.available.names[1],
    data.aws_availability_zones.available.names[2],
  ]

  private_subnets    = var.private_subnets
  public_subnets     = var.public_subnets
  enable_nat_gateway = true
  single_nat_gateway = true

  tags = merge(local.tags, local.cluster_vpc_tags)
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name                = local.cluster_name
  subnets                     = module.vpc.private_subnets
  vpc_id                      = module.vpc.vpc_id
  worker_groups               = module.workers.worker_groups
  cluster_create_timeout      = "15m"
  cluster_delete_timeout      = "15m"
  kubeconfig_name             = local.prefix
  config_output_path          = "${path.module}/"
  workers_additional_policies = module.policies.worker_additional_policies

  tags = merge(local.tags, local.cluster_autoscaler_tags)
}

module "policies" {
  source = "../../modules/policies"
}

module "storage" {
  source      = "../../modules/storage"
  bucket_name = local.prefix
  region      = var.region
  tags        = var.tags
}

module "workers" {
  source                  = "../../modules/workers"
  region                  = var.region
  workers_template        = var.worker_groups_type
  subnets                 = module.vpc.private_subnets
  cpu_instance_type       = var.cpu_instance_type_aws
  cpu_desired_node_count  = var.cpu_desired_node_count
  cpu_max_node_count      = var.cpu_max_node_count
  cpu_min_node_count      = var.cpu_min_node_count
  cpu_autoscaling_enabled = var.cpu_autoscaling_enabled

  gpu_instance_type       = var.gpu_instance_type_aws
  gpu_desired_node_count  = var.gpu_desired_node_count
  gpu_max_node_count      = var.gpu_max_node_count
  gpu_min_node_count      = var.gpu_min_node_count
  gpu_autoscaling_enabled = var.gpu_autoscaling_enabled
}

module "ml_platform" {
  source                    = "../../../modules/ml_platform"
  backend_uri               = module.registry.repositories_uri[0]
  base_build_uri            = module.registry.repositories_uri[1]
  pull_backend_image_policy = var.pull_backend_image_policy
  storage_backend           = "AMAZON"
  gpu_counts                = module.workers.gpu_counts
  cpu_counts                = module.workers.cpu_counts
  memory_counts             = module.workers.memory_counts

  # kubernetes service api
  api_memory_request = var.api_memory_request
  api_memory_limit = var.api_memory_limit
  api_cpu_request = var.api_cpu_request
  api_cpu_limit = var.api_cpu_limit

  pachyderm_tag = var.pachyderm_tag
  token = var.token

  data = {
    amazon-bucket = module.storage.bucket
    amazon-region = module.storage.region
    amazon-secret = var.aws_secret_access_key
    amazon-id     = var.aws_access_key_id
  }

  wait_for_ready_state = true
  scripts_dir          = "${path.module}/../../../../scripts"
  kubeconfig_filename  = module.eks.kubeconfig_filename
  docker_registry      = module.registry.registry_id
  cluster_name         = local.cluster_name
  nodes                = module.workers.nodes
  region               = var.region
}

module "registry" {
  source = "../../modules/registry"

  image_names = [
    "${local.prefix}-backend",
    "${local.prefix}-base-build",
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

  region      = var.region
  scripts_dir = "${path.module}/../../../../scripts"
}

module "output_config" {
  source              = "../../../modules/output_config"
  backend_domain      = module.ml_platform.backend_domain
  backend_port        = module.ml_platform.backend_port
  kubeconfig_filename = module.eks.kubeconfig_filename
  out_dir             = var.config_dir
  backend_path        = module.ml_platform.backend_path
}
