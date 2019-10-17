# define AWS region
# =================

provider "aws" {
  version = ">= 2.6.0"
  region  = var.region
}

provider "external" {
  version = ">= 1.0"
}

provider "kubernetes" {
  load_config_file = true
  config_path      = module.eks.kubeconfig_filename
}

# manually define remote state file on S3
# =======================================
terraform {
  backend "s3" {
    bucket  = "kaos-tf-state"
    key     = "kaos-2.tfstate"
    region  = "eu-central-1"
    encrypt = true
  }
}

