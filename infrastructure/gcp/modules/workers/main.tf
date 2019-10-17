resource "null_resource" "get_cpu_machines" {
  triggers = {
    build_time = timestamp() // to always retrigger
  }
  provisioner "local-exec" {
    // TODO: zone shouldn't matter here, but it would be better to change it to var.project_location,
    // however if project location is not zone e.g europe-west4 it will fail
    command = "echo { $(gcloud compute machine-types describe ${var.cpu_instance_type} --zone europe-west4-a | awk '{print \"\\\"\"substr($1, 1, length($1)-1)\"\\\": \\\"\"$2\"\\\",\"}' | sed '$ s/.$//')} > ${path.module}/cpu"
  }
}

resource "null_resource" "get_gpu_machines" {
  triggers = {
    build_time = timestamp() // to always retrigger
  }
  provisioner "local-exec" {
    // TODO: as above
    command = "echo { $(gcloud compute machine-types describe ${var.gpu_instance_type} --zone europe-west4-a |  awk '{print \"\\\"\"substr($1, 1, length($1)-1)\"\\\": \\\"\"$2\"\\\",\"}' | sed '$ s/.$//')} > ${path.module}/gpu"
  }
}


data "external" "cpus_count" {
  depends_on = [null_resource.get_cpu_machines]
  program    = ["cat", "${path.module}/cpu"]

}

data "external" "gpus_count" {
  depends_on = [null_resource.get_gpu_machines]
  program    = ["cat", "${path.module}/gpu"]

}


resource "null_resource" "read_details" {
  triggers = {
    cpus   = tonumber(data.external.cpus_count.result["guestCpus"]) + (var.worker_groups_type == "cpu_gpu" ? tonumber(data.external.gpus_count.result["guestCpus"]) : 0)
    memory = (tonumber(data.external.cpus_count.result["memoryMb"]) / 1024) + (var.worker_groups_type == "cpu_gpu" ? (tonumber(data.external.gpus_count.result["memoryMb"]) / 1024) : 0)
  }
}