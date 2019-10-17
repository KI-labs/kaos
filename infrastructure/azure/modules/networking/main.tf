resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-${var.network_rg_specs["name"]}"
  location = var.network_rg_specs["location"]
}

resource "azurerm_virtual_network" "network" {
  name                = "${var.prefix}-vnet"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = [var.network_address_space]
}

resource "azurerm_subnet" "subnet" {
  count                = var.subnet_count
  name                 = "${var.prefix}-subnet-${count.index}"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.network.name
  address_prefix       = var.subnet_address_space
}

