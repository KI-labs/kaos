output "worker_groups" {
  value = local.templates[var.workers_template]
}

output "nodes" {
  value = (var.workers_template == "cpu_gpu" ? var.gpu_desired_node_count : 0) + var.cpu_desired_node_count
}

output "gpu_counts" {
  value = [
    for worker in local.templates[var.workers_template] :
    local.resources[worker["instance_type"]]["gpu"]
  ]
}

output "cpu_counts" {
  value = [
    for worker in local.templates[var.workers_template] :
    local.resources[worker["instance_type"]]["cpu"]
  ]
}

output "memory_counts" {
  value = [
    for worker in local.templates[var.workers_template] :
    local.resources[worker["instance_type"]]["memory"]
  ]
}

