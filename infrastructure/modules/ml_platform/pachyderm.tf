resource "kubernetes_secret" "pachyderm_storage_secret" {
  metadata {
    name = "pachyderm-storage-secret"

    labels = {
      app     = "kaos-pachyderm"
      suite   = "pachyderm"
      release = "kaos"
    }
  }

  data       = merge(var.fake_data, var.data)
  depends_on = [null_resource.poll]
}

resource "kubernetes_service_account" "pachyderm" {
  metadata {
    name = "pachyderm"

    labels = {
      app     = "kaos-pachyderm"
      suite   = "pachyderm"
      release = "kaos"
    }
  }

  automount_service_account_token = true
  depends_on                      = [null_resource.poll]
}

resource "kubernetes_cluster_role" "pachyderm" {
  metadata {
    name = "pachyderm"
  }

  rule {
    verbs      = ["get", "list", "watch"]
    api_groups = [""]
    resources  = ["nodes", "pods", "pods/log", "endpoints"]
  }

  rule {
    verbs      = ["get", "list", "watch", "create", "update", "delete"]
    api_groups = [""]
    resources  = ["replicationcontrollers", "services"]
  }

  rule {
    verbs          = ["get", "list", "watch", "create", "update", "delete"]
    api_groups     = [""]
    resources      = ["secrets"]
    resource_names = [kubernetes_secret.pachyderm_storage_secret.metadata[0].name]
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_cluster_role_binding" "pachyderm" {
  metadata {
    name = "pachyderm"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "pachyderm"
  }

  subject {
    kind      = "ServiceAccount"
    name      = "pachyderm"
    namespace = "default"
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_service" "pachd" {
  metadata {
    name = "pachd"

    labels = {
      app     = "pachd"
      release = "kaos"
      suite   = "pachyderm"
    }
  }

  spec {
    port {
      name        = "api-grpc-port"
      port        = 650
      target_port = "650"
      node_port   = 30650
    }

    port {
      name        = "trace-port"
      port        = 651
      target_port = "651"
      node_port   = 30651
    }

    port {
      name        = "api-http-port"
      port        = 652
      target_port = "652"
      node_port   = 30652
    }

    selector = {
      app = "pachd"
    }

    type = "NodePort"
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_deployment" "pachd" {
  metadata {
    name = "pachd"

    labels = {
      app     = "pachd"
      suite   = "pachyderm"
      release = "kaos"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        suite = "pachyderm"
        app   = "pachd"
      }
    }

    template {
      metadata {
        name = "pachd"

        labels = {
          app   = "pachd"
          suite = "pachyderm"
        }
      }

      spec {
        service_account_name = kubernetes_service_account.pachyderm.metadata[0].name

        volume {
          name = kubernetes_service_account.pachyderm.default_secret_name

          secret {
            secret_name = kubernetes_service_account.pachyderm.default_secret_name
          }
        }

        volume {
          name = "pachdvol"

          host_path {
            path = "/var/pachyderm/pachd"
          }
        }

        volume {
          name = kubernetes_secret.pachyderm_storage_secret.metadata[0].name

          secret {
            secret_name = kubernetes_secret.pachyderm_storage_secret.metadata[0].name
          }
        }

        container {
          name  = "pachd"
          image = "pachyderm/pachd:${var.pachyderm_tag}"

          port {
            name           = "api-grpc-port"
            container_port = 650
            protocol       = "TCP"
          }

          port {
            name           = "trace-port"
            container_port = 651
          }

          port {
            name           = "api-http-port"
            container_port = 652
          }

          env {
            name  = "PACH_ROOT"
            value = "/pach"
          }

          env {
            name  = "NUM_SHARDS"
            value = "16"
          }

          env {
            name  = "STORAGE_BACKEND"
            value = var.storage_backend
          }

          env {
            name  = "STORAGE_HOST_PATH"
            value = "/var/pachyderm/pachd"
          }

          env {
            name = "PACHD_POD_NAMESPACE"

            value_from {
              field_ref {
                api_version = "v1"
                field_path  = "metadata.namespace"
              }
            }
          }

          env {
            name  = "WORKER_IMAGE"
            value = "pachyderm/worker:${var.pachyderm_tag}"
          }

          env {
            name  = "WORKER_SIDECAR_IMAGE"
            value = "pachyderm/pachd:${var.pachyderm_tag}"
          }

          env {
            name  = "WORKER_IMAGE_PULL_POLICY"
            value = "IfNotPresent"
          }

          env {
            name  = "PACHD_VERSION"
            value = var.pachyderm_tag
          }

          env {
            name  = "METRICS"
            value = "true"
          }

          env {
            name  = "LOG_LEVEL"
            value = "info"
          }

          env {
            name  = "BLOCK_CACHE_BYTES"
            value = "0G"
          }

          env {
            name = "IAM_ROLE"
          }

          env {
            name  = "PACHYDERM_AUTHENTICATION_DISABLED_FOR_TESTING"
            value = "false"
          }

          env {
            name = "AMAZON_ID"

            value_from {
              secret_key_ref {
                key  = "amazon-id"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "AMAZON_SECRET"

            value_from {
              secret_key_ref {
                key  = "amazon-secret"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "AMAZON_REGION"

            value_from {
              secret_key_ref {
                key  = "amazon-region"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "AMAZON_BUCKET"

            value_from {
              secret_key_ref {
                key  = "amazon-bucket"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "GOOGLE_CRED"

            value_from {
              secret_key_ref {
                key  = "google-cred"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "GOOGLE_BUCKET"

            value_from {
              secret_key_ref {
                key  = "google-bucket"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "MICROSOFT_ID"

            value_from {
              secret_key_ref {
                key  = "microsoft-id"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "MICROSOFT_SECRET"

            value_from {
              secret_key_ref {
                key  = "microsoft-secret"
                name = "pachyderm-storage-secret"
              }
            }
          }

          env {
            name = "MICROSOFT_CONTAINER"

            value_from {
              secret_key_ref {
                key  = "microsoft-container"
                name = "pachyderm-storage-secret"
              }
            }
          }

          resources {
            requests {
              cpu    = "250m"
              memory = "512M"
            }
          }

          volume_mount {
            name       = "pachdvol"
            mount_path = "/pach"
          }

          volume_mount {
            name       = kubernetes_secret.pachyderm_storage_secret.metadata[0].name
            mount_path = "/pachyderm-storage-secret"
          }

          volume_mount {
            mount_path = "/var/run/secrets/kubernetes.io/serviceaccount"
            name       = kubernetes_service_account.pachyderm.default_secret_name
            read_only  = true
          }

          image_pull_policy = "Always"

          security_context {
            privileged = true
          }
        }
      }
    }
  }

  depends_on = [null_resource.poll]
}
