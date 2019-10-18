resource "azurerm_resource_group" "storage_rg" {
  name     = "${var.prefix}-${var.storage_rg_specs["name"]}"
  location = var.storage_rg_specs["location"]
}

resource "azurerm_storage_account" "storage_account" {
  name                     = "${var.tags["project"]}${var.tags["env"]}"
  resource_group_name      = azurerm_resource_group.storage_rg.name
  location                 = azurerm_resource_group.storage_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = var.tags
}

resource "azurerm_storage_container" "storage_container" {
  name                  = var.prefix
  resource_group_name   = azurerm_resource_group.storage_rg.name
  storage_account_name  = azurerm_storage_account.storage_account.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "storage_blob" {
  name = var.prefix

  resource_group_name    = azurerm_resource_group.storage_rg.name
  storage_account_name   = azurerm_storage_account.storage_account.name
  storage_container_name = azurerm_storage_container.storage_container.name

  type = "page"
  size = 5120
}

