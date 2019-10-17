resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-images"
  location = var.region
}

resource "azurerm_container_registry" "registry" {
  count               = length(var.image_names)
  name                = element(var.image_names, count.index)
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Standard"
  admin_enabled       = true
}

data "external" "md5" {
  count   = length(var.image_names)
  program = ["bash", "${var.scripts_dir}/md5.sh"]

  query = {
    path = element(var.docker_contexts, count.index)
  }
}

resource "null_resource" "build_push_tag" {
  count = length(var.image_names)

  triggers = {
    url = element(azurerm_container_registry.registry.*.name, count.index)
    md5 = element(data.external.md5.*.result.md5, count.index)
  }

  provisioner "local-exec" {
    command = "sh ${var.scripts_dir}/azure/build_push_tag.sh -c=${element(var.docker_contexts, count.index)} -f=${element(var.docker_files, count.index)} -i=${element(var.image_names, count.index)} -t=${element(var.image_tags, count.index)} -u=${element(
      azurerm_container_registry.registry.*.admin_username,
      count.index,
      )} -p=${element(
      azurerm_container_registry.registry.*.admin_password,
      count.index,
    )}"
  }

  depends_on = [
    data.external.md5,
    azurerm_container_registry.registry,
  ]
}

