provider "azurerm" {
  subscription_id = var.SUBSCRIPTION_ID
  client_id       = var.CLIENT_ID
  client_secret   = var.CLIENT_SECRET
  tenant_id       = var.TENANT_ID
  version         = "~> 1.6"
}

terraform {
  backend "azurerm" {
    storage_account_name = "kaostfstate"
    container_name       = "tstate"
    key                  = "terraform.tfstate"
  }
}

provider "kubernetes" {
  version          = "~> 1.6.2"
  load_config_file = true
  config_path      = module.kubernetes.kubeconfig_filename
}

