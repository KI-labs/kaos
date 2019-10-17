

provider "google" {
  credentials = file(var.credentials_path)
  project     = var.gcp_project_name
  region      = var.project_location
}


terraform {
  backend "local" {}
}

data "google_client_config" "current" {
}

provider "kubernetes" {
  load_config_file       = false
  host                   = module.kubernetes.cluster_endpoint
  cluster_ca_certificate = base64decode(module.kubernetes.cluster_ca_certificate)
  token                  = data.google_client_config.current.access_token
}

