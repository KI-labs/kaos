output "image_uri" {
  value = formatlist("%s:%s", var.image_names, var.image_tags)
}
