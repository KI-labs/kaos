output "image_uri" {
  value = formatlist(
    "%s.azurecr.io/%s:%s",
    var.image_names,
    var.image_names,
    var.image_tags,
  )
}

output "registry_name" {
  value = "${element(var.image_names, 0)}.azurecr.io"
}

output "registry_id" {
  value = element(azurerm_container_registry.registry.*.id, 0)
}

output "registry_username" {
  value = element(azurerm_container_registry.registry.*.admin_username, 0)
}

output "registry_password" {
  value = element(azurerm_container_registry.registry.*.admin_password, 0)
}

