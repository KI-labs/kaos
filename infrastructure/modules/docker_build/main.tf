data "external" "md5" {
  count   = length(var.image_names)
  program = ["bash", "${var.scripts_dir}/md5.sh"]

  query = {
    path = var.docker_contexts[count.index]
  }
}

resource "null_resource" "build_push_tag" {
  count = length(var.image_names)

  triggers = {
    md5 = data.external.md5.*.result.md5[count.index]
  }

  provisioner "local-exec" {
    command = "bash ${var.scripts_dir}/local/build.sh -c=${element(var.docker_contexts, count.index)} -f=${element(var.docker_files, count.index)} -i=${element(var.image_names, count.index)} -t=${element(var.image_tags, count.index)} ${var.is_minikube ? "--minikube" : ""}"
  }

  depends_on = ["data.external.md5"]
}
