output "nodes" {
  value = (var.worker_groups_type == "cpu_gpu" ? var.gpu_desired_node_count : 0) + var.cpu_desired_node_count
}

output "gpu_counts" {
  value = [var.worker_groups_type == "cpu_gpu" ? var.gpu_accelerator_count : 0]
}

output "cpu_counts" {
  value = [null_resource.read_details.triggers.cpus]
}
//
output "memory_counts" {
  value = [null_resource.read_details.triggers.memory]
}

