locals {
  prefix       = "${var.tags["project"]}-${var.tags["version"]}-${terraform.workspace}"
  cluster_name = "${var.tags["project"]}-${var.tags["version"]}-${terraform.workspace}-eks-cluster"

  cluster_autoscaler_tags = {
    "k8s.io/cluster-autoscaler"         = "true"
    "k8s.io/cluster-autoscaler/enabled" = "true"
  }

  cluster_vpc_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared",
    "kubernetes.io/role/internal-elb"             = "true"
  }

  tags = var.tags
}

