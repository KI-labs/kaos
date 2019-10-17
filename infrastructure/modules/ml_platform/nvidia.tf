resource "kubernetes_daemonset" "nvidia_device_plugin_daemonset_amazon" {
  count = length(var.gpu_counts) > 0 && var.storage_backend == "AMAZON" ? 1 : 0

  metadata {
    name      = "nvidia-device-plugin-daemonset"
    namespace = "kube-system"
  }

  spec {

    selector {
      match_labels = {
        name = "nvidia-device-plugin-ds"
      }
    }

    template {

      metadata {
        labels = {
          name = "nvidia-device-plugin-ds"
        }

        annotations = {
          "scheduler.alpha.kubernetes.io/critical-pod" = ""
        }
      }

      spec {

        toleration {
          key      = "CriticalAddonsOnly"
          operator = "Exists"
        }

        toleration {
          key      = "nvidia.com/gpu"
          operator = "Exists"
          effect   = "NoSchedule"
        }

        volume {
          name = "device-plugin"
          host_path {
            path = "/var/lib/kubelet/device-plugins"
          }
        }

        container {
          name  = "nvidia-device-plugin-ctr"
          image = "nvidia/k8s-device-plugin:1.0.0-beta"

          volume_mount {
            name       = "device-plugin"
            mount_path = "/var/lib/kubelet/device-plugins"
          }

        }
      }
    }

    strategy {
      type = "RollingUpdate"
    }

  }
}

resource "kubernetes_daemonset" "nvidia_device_plugin_daemonset_google" {
  count = length(var.gpu_counts) > 0 && var.storage_backend == "GOOGLE" ? 1 : 0

  metadata {
    name      = "nvidia-device-plugin-daemonset"
    namespace = "kube-system"
  }

  spec {

    selector {
      match_labels = {
        name = "nvidia-driver-installer"
      }
    }

    template {

      metadata {
        labels = {
          name    = "nvidia-driver-installer"
          k8s-app = "nvidia-driver-installer"
        }

      }

      spec {
        affinity {
          node_affinity {
            required_during_scheduling_ignored_during_execution {
              node_selector_term {
                match_expressions {
                  key      = "cloud.google.com/gke-accelerator"
                  operator = "Exists"
                }
              }
            }
          }
        }
        toleration {
          operator = "Exists"
        }

        host_network = true
        host_pid     = true

        volume {
          name = "dev"
          host_path {
            path = "/dev"
          }
        }


        volume {
          name = "nvidia-install-dir-host"
          host_path {
            path = "/home/kubernetes/bin/nvidia"
          }
        }


        volume {
          name = "root-mount"
          host_path {
            path = "/"
          }
        }

        init_container {
          name              = "nvidia-driver-installer"
          image             = "cos-nvidia-installer:fixed"
          image_pull_policy = "Never"
          resources {
            requests {
              cpu = 0.15
            }
          }
          security_context {
            privileged = true
          }
          env {
            name  = "NVIDIA_INSTALL_DIR_HOST"
            value = "/home/kubernetes/bin/nvidia"
          }
          env {
            name  = "NVIDIA_INSTALL_DIR_CONTAINER"
            value = "/usr/local/nvidia"
          }
          env {
            name  = "ROOT_MOUNT_DIR"
            value = "/root"
          }
          volume_mount {
            mount_path = "/usr/local/nvidia"
            name       = "nvidia-install-dir-host"
          }
          volume_mount {
            mount_path = "/dev"
            name       = "dev"
          }
          volume_mount {
            mount_path = "/root"
            name       = "root-mount"
          }
        }

        container {
          name  = "pause"
          image = "gcr.io/google-containers/pause:2.0"

        }
      }
    }

  }
}
