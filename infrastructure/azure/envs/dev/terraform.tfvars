tags = {
  project = "kaos"
  env     = "dev"
  version = "2"
}

k8s_vm_size = "Standard_D2s_v3"

k8s_network_cidr = "180.0.0.0/16"

k8s_subnet_cidr = "180.0.1.0/24"

os_disk_size_in_gb = "30"

worker_node_count = "1"

## Storage Variables
storage_account_name = "internal"

storage_rg_specs = {
  name     = "internal-rg"
  location = "westeurope"
}

## Networking Variables
network_rg_specs = {
  name     = "net-rg"
  location = "westeurope"
}

network_address_space = "12.0.0.0/16"

subnet_address_space = "12.0.1.0/24"

subnet_count = 1
