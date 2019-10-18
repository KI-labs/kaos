output "gcr_location" {
  value = data.google_container_registry_image.images.*.image_url
}

output "google_cloud_registry_id" {
  value = data.google_container_registry_repository.gcp_registry.id
}

