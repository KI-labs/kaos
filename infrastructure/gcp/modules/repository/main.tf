data "google_container_registry_repository" "gcp_registry" {
  region = var.region
}

data "google_container_registry_image" "images" {
  region = var.region
  count  = length(var.image_names)
  name   = element(var.image_names, count.index)
}

data "external" "md5" {
  count = length(var.docker_contexts)

  program = [
    "bash",
    "${var.scripts_dir}/md5.sh",
  ]

  query = {
    path = element(var.docker_contexts, count.index)
  }
}

resource "null_resource" "login_registry" {
  triggers = {
    url = data.google_container_registry_repository.gcp_registry.repository_url
    md5 = join("-", data.external.md5.*.result.md5)
  }

  provisioner "local-exec" {
    command = "sh ${var.scripts_dir}/gcp/login_registry.sh -a=${var.credentials_path} -r=${var.region}"
  }

  depends_on = [
    data.external.md5,
    data.google_container_registry_repository.gcp_registry,
  ]
}

resource "null_resource" "build_push_tag" {
  count = length(var.image_names)

  triggers = {
    url = data.google_container_registry_repository.gcp_registry.repository_url
    md5 = element(data.external.md5.*.result.md5, count.index)
  }

  provisioner "local-exec" {
    command = "sh ${var.scripts_dir}/gcp/build_push_tag.sh -c=${element(var.docker_contexts, count.index)} -f=${element(var.docker_files, count.index)} -i=${element(var.image_names, count.index)} -t=${element(var.image_tags, count.index)} -p=${var.project_name}"
  }

  depends_on = [null_resource.login_registry]
}

