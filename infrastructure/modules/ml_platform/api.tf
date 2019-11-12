resource "kubernetes_service" "api" {
  metadata {
    name = "backend"

    annotations = {
      "getambassador.io/config" = <<EOF
        apiVersion: ambassador/v1
        kind:  Mapping
        name:  api_mapping
        prefix: /api/
        service: backend:80
        timeout_ms: 30000000
        idle_timeout_ms: 50000000
        connect_timeout_ms: 40000000
        
EOF

    }

    labels = {
      app     = "kaos-backend"
      suite   = "api"
      release = "kaos"
    }
  }

  spec {
    port {
      name        = "http-port"
      port        = "80"
      target_port = "8080"
    }

    selector = {
      app = "kaos-backend"
    }

    type = "ClusterIP"
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_deployment" "api" {
  metadata {
    name = "backend"

    labels = {
      app     = "kaos-backend"
      suite   = "api"
      release = "kaos"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app   = "kaos-backend"
        suite = "api"
      }
    }

    template {
      metadata {
        name = "backend"

        labels = {
          app   = "kaos-backend"
          suite = "api"
        }
      }

      spec {
        container {
          name  = "kaos-backend"
          image = var.backend_uri

          port {
            container_port = 8080
          }

          env {
            name  = "BUILD_IMAGE"
            value = var.base_build_uri
          }

          env {
            name  = "DOCKER_REGISTRY"
            value = var.docker_registry
          }

          env {
            name  = "CLOUD_PROVIDER"
            value = var.cloud_provider[var.storage_backend]
          }

          env {
            name  = "REGION"
            value = var.region
          }

          env {
            name  = "MAX_GPU"
            value = max(var.gpu_counts...)
          }

          env {
            name  = "MAX_CPU"
            value = max(var.cpu_counts...)
          }

          env {
            name  = "MAX_MEMORY"
            value = max(var.memory_counts...)
          }

          env {
            name  = "SERVICE_HOSTNAME"
            value = var.ambassador_service_type == "LoadBalancer" ? kubernetes_service.ambassador.load_balancer_ingress[0].hostname : ""
          }

          env {
            name  = "SERVICE_IP"
            value = var.ambassador_service_type == "LoadBalancer" ? kubernetes_service.ambassador.load_balancer_ingress[0].ip : kubernetes_service.ambassador.spec[0].cluster_ip
          }

          env {
            name  = "TOKEN"
            value = var.token
          }

          resources {
            limits {
              memory = var.api_memory_limit
              cpu = var.api_cpu_limit
            }

            requests {
              memory = var.api_memory_request
              cpu = var.api_cpu_request
            }
          }

          image_pull_policy = var.pull_backend_image_policy
        }

        image_pull_secrets {
          name = kubernetes_secret.docker_registry.metadata[0].name
        }
      }
    }
  }

  depends_on = [null_resource.poll]
}
