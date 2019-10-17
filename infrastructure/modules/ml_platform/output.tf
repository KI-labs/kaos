output "backend_domain" {
  value = kubernetes_service.ambassador.load_balancer_ingress
}

output "backend_port" {
  value = "80"
}

output "backend_path" {
  value = "/api/"
}

