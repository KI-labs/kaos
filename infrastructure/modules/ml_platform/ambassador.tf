resource "kubernetes_service" "ambassador_admin" {
  metadata {
    name = "ambassador-admin"

    labels = {
      service = "ambassador-admin"
    }
  }

  spec {
    port {
      name        = "ambassador-admin"
      port        = 8877
      target_port = "8877"
    }

    selector = {
      service = "ambassador"
    }

    type = var.ambassador_admin_service_type
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_service" "ambassador" {
  metadata {
    name = "ambassador"
    annotations = {
      # FIXME – timeout is a temporary workaround
      "service.beta.kubernetes.io/aws-load-balancer-connection-idle-timeout" = "3600"
    }
  }

  spec {
    port {
      port        = 80
      target_port = "8080"
    }

    selector = {
      service = "ambassador"
    }

    type = var.ambassador_service_type
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_cluster_role" "ambassador" {
  metadata {
    name = "ambassador"
  }

  rule {
    verbs      = ["get", "list", "watch"]
    api_groups = [""]
    resources  = ["namespaces", "services", "secrets", "endpoints"]
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_service_account" "ambassador" {
  metadata {
    name = "ambassador"
  }

  automount_service_account_token = "true"

  depends_on = [null_resource.poll]
}

resource "kubernetes_cluster_role_binding" "ambassador" {
  metadata {
    name = "ambassador"
  }

  subject {
    kind      = "ServiceAccount"
    name      = "ambassador"
    namespace = "default"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "ambassador"
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_deployment" "ambassador" {
  metadata {
    name = "ambassador"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        "service" = "ambassador"
      }
    }

    template {
      metadata {
        labels = {
          "service" = "ambassador"
        }

        annotations = {
          "consul.hashicorp.com/connect-inject" = "false"
          "sidecar.istio.io/inject"             = "false"
        }
      }

      spec {
        service_account_name = kubernetes_service_account.ambassador.metadata[0].name

        volume {
          name = kubernetes_service_account.ambassador.default_secret_name

          secret {
            secret_name = kubernetes_service_account.ambassador.default_secret_name
          }
        }

        container {
          name  = "ambassador"
          image = "quay.io/datawire/ambassador:0.72.0"

          port {
            name           = "http"
            container_port = 8080
          }

          port {
            name           = "https"
            container_port = 8443
          }

          port {
            name           = "admin"
            container_port = 8877
          }

          env {
            name = "AMBASSADOR_NAMESPACE"

            value_from {
              field_ref {
                field_path = "metadata.namespace"
              }
            }
          }

          resources {
            limits {
              memory = "400Mi"
              cpu    = "1"
            }

            requests {
              cpu    = "200m"
              memory = "100Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/ambassador/v0/check_alive"
              port = "8877"
            }

            initial_delay_seconds = 30
            period_seconds        = 3
          }

          readiness_probe {
            http_get {
              path = "/ambassador/v0/check_ready"
              port = "8877"
            }

            initial_delay_seconds = 30
            period_seconds        = 3
          }

          volume_mount {
            mount_path = "/var/run/secrets/kubernetes.io/serviceaccount"
            name       = kubernetes_service_account.ambassador.default_secret_name
            read_only  = true
          }
        }

        restart_policy = "Always"

        security_context {
          run_as_user = 8888
        }
      }
    }
  }

  depends_on = [null_resource.poll]
}

