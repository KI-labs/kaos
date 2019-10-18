resource "azurerm_virtual_network" "k8s-network" {
  name                = "${var.prefix}-vnet"
  location            = azurerm_resource_group.k8s.location
  resource_group_name = azurerm_resource_group.k8s.name
  address_space       = [var.k8s_network_cidr]
}

resource "azurerm_subnet" "k8s-subnet" {
  name                 = "${var.prefix}-vnet-subnet"
  resource_group_name  = azurerm_resource_group.k8s.name
  virtual_network_name = azurerm_virtual_network.k8s-network.name
  address_prefix       = var.k8s_subnet_cidr
}

