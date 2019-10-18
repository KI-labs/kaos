resource "aws_ecr_repository" "repository" {
  count = length(var.image_names)
  name  = var.image_names[count.index]
}

data "external" "md5" {
  count   = length(var.image_names)
  program = ["bash", "${var.scripts_dir}/md5.sh"]

  query = {
    path = var.docker_contexts[count.index]
  }
}

resource "null_resource" "login_registry" {
  triggers = {
    url = join("-", aws_ecr_repository.repository.*.repository_url)
    md5 = join("-", data.external.md5.*.result.md5)
  }

  provisioner "local-exec" {
    command = "bash ${var.scripts_dir}/aws/login_registry.sh -r=${var.region}"
  }

  depends_on = [
    data.external.md5,
    aws_ecr_repository.repository,
  ]
}

resource "null_resource" "build_push_tag" {
  count = length(var.image_names)

  triggers = {
    url = aws_ecr_repository.repository.*.repository_url[count.index]
    md5 = data.external.md5.*.result.md5[count.index]
  }

  provisioner "local-exec" {
    command = "bash ${var.scripts_dir}/aws/build_push_tag.sh -c=${element(var.docker_contexts, count.index)} -f=${element(var.docker_files, count.index)} -i=${element(aws_ecr_repository.repository.*.name, count.index)} -t=${element(var.image_tags, count.index)} -r=${var.region}"
  }

  depends_on = [null_resource.login_registry]
}

