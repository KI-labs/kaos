provider "aws" {
  region = "${var.region}"
}

provider "external" {
  version = "1.1.1"
}

data "aws_availability_zones" "available" {}

locals {
  prefix = "${var.tags["project"]}-${var.tags["version"]}-${var.tags["env"]}"
}

module "network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "1.60.0"
  name    = "${local.prefix}-vpc"
  cidr    = "${var.main_cidr}"

  azs = ["${data.aws_availability_zones.available.names[0]}", "${data.aws_availability_zones.available.names[1]}"]

  private_subnets    = ["10.0.1.0/24", "10.0.3.0/24"]
  public_subnets     = ["10.0.2.0/24", "10.0.4.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = true

  tags = "${var.tags}"
}

module "storage" {
  source = "../../modules/storage"

  bucket_name = "${local.prefix}"

  tags = "${var.tags}"
}

module "security_groups" {
  source = "../../modules/security_groups"
  vpc_id = "${module.network.vpc_id}"
  prefix = "${local.prefix}"
  tags   = "${var.tags}"
}

module "eks" {
  source       = "terraform-aws-modules/eks/aws"
  cluster_name = "${local.prefix}-eks-cluster"
  subnets      = ["${module.network.private_subnets}"]
  vpc_id       = "${module.network.vpc_id}"

  worker_groups = [{
    # This will launch an autoscaling group with only On-Demand instances
    instance_type        = "${var.on_demand_instance_type}"
    subnets              = "${join(",", module.network.private_subnets)}"
    asg_desired_capacity = "${var.on_demand_asg_desired_capacity}"
  }]

  worker_group_count                   = "1"
  worker_additional_security_group_ids = ["${module.security_groups.all_worker_id}"]
  kubeconfig_name                      = "${local.prefix}"
  write_aws_auth_config                = true
  workers_additional_policies_count    = "1"
  workers_additional_policies          = ["arn:aws:iam::aws:policy/AmazonS3FullAccess"]
  tags                                 = "${var.tags}"
}

module "registry" {
  source         = "../../modules/registry"
  image_names    = "${local.prefix}-backend"
  image_tags     = "latest"
  scripts_dir    = "../../scripts"
  docker_context = "../../backend"
  region         = "${var.region}"
}
