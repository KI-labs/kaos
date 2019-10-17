resource "google_storage_bucket" "kaos-feature-store" {
  name          = var.bucket_name
  location      = var.bucket_location
  force_destroy = true
}

