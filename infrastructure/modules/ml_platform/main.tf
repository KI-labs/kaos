resource "null_resource" "poll" {
  count = var.wait_for_ready_state ? 1 : 0

  provisioner "local-exec" {
    command = "bash ${var.scripts_dir}/poll_cluster.sh -k=${var.kubeconfig_filename} -t=${var.timeout} -i=${var.interval} -n=${var.nodes}"
  }
}

resource "kubernetes_service" "etcd" {
  metadata {
    name = "etcd"

    labels = {
      suite   = "pachyderm"
      app     = "kaos-etcd"
      release = "kaos"
    }
  }

  spec {
    port {
      name = "client-port"
      port = 2379
    }

    selector = {
      app = "kaos-etcd"
    }

    type = "NodePort"
  }
  depends_on = [null_resource.poll]
}

resource "kubernetes_deployment" "etcd" {
  metadata {
    name = "etcd"

    labels = {
      app     = "kaos-etcd"
      suite   = "pachyderm"
      release = "kaos"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app   = "kaos-etcd"
        suite = "pachyderm"
      }
    }

    template {
      metadata {
        name = "etcd"

        labels = {
          app   = "kaos-etcd"
          suite = "pachyderm"
        }
      }

      spec {
        volume {
          name = "etcdvol"

          host_path {
            path = "/var/pachyderm/etcd"
          }
        }

        container {
          name  = "etcd"
          image = "quay.io/coreos/etcd:v3.3.5"

          command = [
            "/usr/local/bin/etcd",
            "--listen-client-urls=http://0.0.0.0:2379",
            "--advertise-client-urls=http://0.0.0.0:2379",
            "--data-dir=/var/data/etcd",
            "--auto-compaction-retention=1",
            "--max-txn-ops=5000",
          ]

          port {
            name           = "client-port"
            container_port = 2379
          }

          port {
            name           = "peer-port"
            container_port = 2380
          }

          resources {
            requests {
              cpu    = "250m"
              memory = "256M"
            }
          }

          volume_mount {
            name       = "etcdvol"
            mount_path = "/var/data/etcd"
          }

          image_pull_policy = "IfNotPresent"
        }
      }
    }
  }

  depends_on = [null_resource.poll]
}

locals {
  dockerconfigjson = {
    auths = {
      "var.docker_registry" = {
        username = var.docker_username
        password = var.docker_password
        email    = var.docker_email
        auth     = base64encode("${var.docker_username}:${var.docker_password}")
      }
    }
  }

  depends_on = [null_resource.poll]
}

resource "kubernetes_secret" "docker_registry" {
  metadata {
    name = "backend-registry-secret"

    labels = {
      app     = "kaos-backend"
      suite   = "api"
      release = "kaos"
    }
  }

  data = {
    ".dockerconfigjson" = jsonencode(local.dockerconfigjson)
  }

  type       = "kubernetes.io/dockerconfigjson"
  depends_on = [null_resource.poll]
}
