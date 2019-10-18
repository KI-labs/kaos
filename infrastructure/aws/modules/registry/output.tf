output "repositories_uri" {
  value = formatlist(
    "%s:%s",
    aws_ecr_repository.repository.*.repository_url,
    var.image_tags,
  )
}

output "registry_id" {
  value = element(
    split("/", aws_ecr_repository.repository[0].repository_url),
    0,
  )
}

