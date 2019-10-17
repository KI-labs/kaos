locals {
  templates = {
    cpu_only = [
      {
        subnets              = var.subnets
        instance_type        = var.cpu_instance_type
        asg_desired_capacity = var.cpu_desired_node_count
        asg_max_size         = var.cpu_max_node_count
        asg_min_size         = var.cpu_min_node_count
        autoscaling_enabled  = var.cpu_autoscaling_enabled
      }
    ]

    cpu_gpu = [
      {
        subnets              = var.subnets
        instance_type        = var.cpu_instance_type
        asg_desired_capacity = var.cpu_desired_node_count
        asg_max_size         = var.cpu_max_node_count
        asg_min_size         = var.cpu_min_node_count
        autoscaling_enabled  = var.cpu_autoscaling_enabled
      },
      {
        subnets              = var.subnets
        ami_id               = lookup(local.gpu_ami_id_by_region, var.region, "ami-0641def7f02a4cac5")
        instance_type        = var.gpu_instance_type
        asg_desired_capacity = var.gpu_desired_node_count
        asg_max_size         = var.gpu_max_node_count
        asg_min_size         = var.gpu_min_node_count
        autoscaling_enabled  = var.gpu_autoscaling_enabled
      }
    ]
  }

  resources = {
    "a1.medium"     = { cpu = 1, memory = 2, gpu = 0 },
    "a1.large"      = { cpu = 2, memory = 4, gpu = 0 },
    "a1.xlarge"     = { cpu = 4, memory = 8, gpu = 0 },
    "a1.2xlarge"    = { cpu = 8, memory = 16, gpu = 0 },
    "a1.4xlarge"    = { cpu = 16, memory = 32, gpu = 0 },
    "t3.nano"       = { cpu = 2, memory = 0.5, gpu = 0 },
    "t3.micro"      = { cpu = 2, memory = 1, gpu = 0 },
    "t3.small"      = { cpu = 2, memory = 2, gpu = 0 },
    "t3.medium"     = { cpu = 2, memory = 4, gpu = 0 },
    "t3.large"      = { cpu = 2, memory = 8, gpu = 0 },
    "t3.xlarge"     = { cpu = 4, memory = 16, gpu = 0 },
    "t3.2xlarge"    = { cpu = 8, memory = 32, gpu = 0 },
    "t3a.nano"      = { cpu = 2, memory = 0.5, gpu = 0 },
    "t3a.micro"     = { cpu = 2, memory = 1, gpu = 0 },
    "t3a.small"     = { cpu = 2, memory = 2, gpu = 0 },
    "t3a.medium"    = { cpu = 2, memory = 4, gpu = 0 },
    "t3a.large"     = { cpu = 2, memory = 8, gpu = 0 },
    "t3a.xlarge"    = { cpu = 4, memory = 16, gpu = 0 },
    "t3a.2xlarge"   = { cpu = 8, memory = 32, gpu = 0 },
    "t2.nano"       = { cpu = 1, memory = 0.5, gpu = 0 },
    "t2.micro"      = { cpu = 1, memory = 1, gpu = 0 },
    "t2.small"      = { cpu = 1, memory = 2, gpu = 0 },
    "t2.medium"     = { cpu = 2, memory = 4, gpu = 0 },
    "t2.large"      = { cpu = 2, memory = 8, gpu = 0 },
    "t2.xlarge"     = { cpu = 4, memory = 16, gpu = 0 },
    "t2.2xlarge"    = { cpu = 8, memory = 32, gpu = 0 },
    "m5.large"      = { cpu = 2, memory = 8, gpu = 0 },
    "m5.xlarge"     = { cpu = 4, memory = 16, gpu = 0 },
    "m5.2xlarge"    = { cpu = 8, memory = 32, gpu = 0 },
    "m5.4xlarge"    = { cpu = 16, memory = 64, gpu = 0 },
    "m5.8xlarge"    = { cpu = 32, memory = 128, gpu = 0 },
    "m5.12xlarge"   = { cpu = 48, memory = 192, gpu = 0 },
    "m5.16xlarge"   = { cpu = 64, memory = 256, gpu = 0 },
    "m5.24xlarge"   = { cpu = 96, memory = 384, gpu = 0 },
    "m5.metal"      = { cpu = 96, memory = 384, gpu = 0 },
    "m5a.large"     = { cpu = 2, memory = 8, gpu = 0 },
    "m5a.xlarge"    = { cpu = 4, memory = 16, gpu = 0 },
    "m5a.2xlarge"   = { cpu = 8, memory = 32, gpu = 0 },
    "m5a.4xlarge"   = { cpu = 16, memory = 64, gpu = 0 },
    "m5a.8xlarge"   = { cpu = 32, memory = 128, gpu = 0 },
    "m5a.12xlarge"  = { cpu = 48, memory = 192, gpu = 0 },
    "m5a.16xlarge"  = { cpu = 64, memory = 256, gpu = 0 },
    "m5a.24xlarge"  = { cpu = 96, memory = 384, gpu = 0 },
    "m5ad.large"    = { cpu = 2, memory = 8, gpu = 0 },
    "m5ad.xlarge"   = { cpu = 4, memory = 16, gpu = 0 },
    "m5ad.2xlarge"  = { cpu = 8, memory = 32, gpu = 0 },
    "m5ad.4xlarge"  = { cpu = 16, memory = 64, gpu = 0 },
    "m5ad.12xlarge" = { cpu = 48, memory = 192, gpu = 0 },
    "m5ad.24xlarge" = { cpu = 96, memory = 384, gpu = 0 },
    "m5d.large"     = { cpu = 2, memory = 8, gpu = 0 },
    "m5d.xlarge"    = { cpu = 4, memory = 16, gpu = 0 },
    "m5d.2xlarge"   = { cpu = 8, memory = 32, gpu = 0 },
    "m5d.4xlarge"   = { cpu = 16, memory = 64, gpu = 0 },
    "m5d.8xlarge"   = { cpu = 32, memory = 128, gpu = 0 },
    "m5d.12xlarge"  = { cpu = 48, memory = 192, gpu = 0 },
    "m5d.16xlarge"  = { cpu = 64, memory = 256, gpu = 0 },
    "m5d.24xlarge"  = { cpu = 96, memory = 384, gpu = 0 },
    "m5d.metal"     = { cpu = 96, memory = 384, gpu = 0 },
    "m4.large"      = { cpu = 2, memory = 8, gpu = 0 },
    "m4.xlarge"     = { cpu = 4, memory = 16, gpu = 0 },
    "m4.2xlarge"    = { cpu = 8, memory = 32, gpu = 0 },
    "m4.4xlarge"    = { cpu = 16, memory = 64, gpu = 0 },
    "m4.10xlarge"   = { cpu = 40, memory = 160, gpu = 0 },
    "m4.16xlarge"   = { cpu = 64, memory = 256, gpu = 0 },
    "c5.large"      = { cpu = 2, memory = 4, gpu = 0 },
    "c5.xlarge"     = { cpu = 4, memory = 8, gpu = 0 },
    "c5.2xlarge"    = { cpu = 8, memory = 16, gpu = 0 },
    "c5.4xlarge"    = { cpu = 16, memory = 32, gpu = 0 },
    "c5.9xlarge"    = { cpu = 36, memory = 72, gpu = 0 },
    "c5.12xlarge"   = { cpu = 48, memory = 96, gpu = 0 },
    "c5.18xlarge"   = { cpu = 72, memory = 144, gpu = 0 },
    "c5.24xlarge"   = { cpu = 96, memory = 192, gpu = 0 },
    "c5.metal"      = { cpu = 96, memory = 192, gpu = 0 },
    "c5d.large"     = { cpu = 2, memory = 4, gpu = 0 },
    "c5d.xlarge"    = { cpu = 4, memory = 8, gpu = 0 },
    "c5d.2xlarge"   = { cpu = 8, memory = 16, gpu = 0 },
    "c5d.4xlarge"   = { cpu = 16, memory = 32, gpu = 0 },
    "c5d.9xlarge"   = { cpu = 36, memory = 72, gpu = 0 },
    "c5d.18xlarge"  = { cpu = 72, memory = 144, gpu = 0 },
    "c5n.large"     = { cpu = 2, memory = 5.25, gpu = 0 },
    "c5n.xlarge"    = { cpu = 4, memory = 10.5, gpu = 0 },
    "c5n.2xlarge"   = { cpu = 8, memory = 21, gpu = 0 },
    "c5n.4xlarge"   = { cpu = 16, memory = 42, gpu = 0 },
    "c5n.9xlarge"   = { cpu = 36, memory = 96, gpu = 0 },
    "c5n.18xlarge"  = { cpu = 72, memory = 192, gpu = 0 },
    "c5n.metal"     = { cpu = 72, memory = 192, gpu = 0 },
    "c4.large"      = { cpu = 2, memory = 3.75, gpu = 0 },
    "c4.xlarge"     = { cpu = 4, memory = 7.5, gpu = 0 },
    "c4.2xlarge"    = { cpu = 8, memory = 15, gpu = 0 },
    "c4.4xlarge"    = { cpu = 16, memory = 30, gpu = 0 },
    "c4.8xlarge"    = { cpu = 36, memory = 60, gpu = 0 },
    "p3.2xlarge"    = { cpu = 8, memory = 61, gpu = 1 },
    "p3.8xlarge"    = { cpu = 32, memory = 244, gpu = 4 },
    "p3.16xlarge"   = { cpu = 64, memory = 488, gpu = 8 },
    "p3dn24xlarge"  = { cpu = 96, memory = 768, gpu = 8 },
    "p2.xlarge"     = { cpu = 4, memory = 61, gpu = 1 },
    "p2.8xlarge"    = { cpu = 32, memory = 488, gpu = 8 },
    "p2.16xlarge"   = { cpu = 64, memory = 768, gpu = 16 },
    "g3s.xlarge"    = { cpu = 4, memory = 30.5, gpu = 1 },
    "g3.4xlarge"    = { cpu = 16, memory = 122, gpu = 1 },
    "g3.8xlarge"    = { cpu = 32, memory = 244, gpu = 2 },
    "g3.16xlarge"   = { cpu = 64, memory = 488, gpu = 4 },
    "x1.16xlarge"   = { cpu = 64, memory = 976, gpu = 0 },
    "x1.32xlarge"   = { cpu = 128, memory = 1.952, gpu = 0 },
    "x1e.xlarge"    = { cpu = 4, memory = 122, gpu = 0 },
    "x1e.2xlarge"   = { cpu = 8, memory = 244, gpu = 0 },
    "x1e.4xlarge"   = { cpu = 16, memory = 488, gpu = 0 },
    "x1e.8xlarge"   = { cpu = 32, memory = 976, gpu = 0 },
    "x1e.16xlarge"  = { cpu = 64, memory = 1.952, gpu = 0 },
    "x1e.32xlarge"  = { cpu = 128, memory = 3.904, gpu = 0 },
    "r5.large"      = { cpu = 2, memory = 16, gpu = 0 },
    "r5.xlarge"     = { cpu = 4, memory = 32, gpu = 0 },
    "r5.2xlarge"    = { cpu = 8, memory = 64, gpu = 0 },
    "r5.4xlarge"    = { cpu = 16, memory = 128, gpu = 0 },
    "r5.8xlarge"    = { cpu = 32, memory = 256, gpu = 0 },
    "r5.12xlarge"   = { cpu = 48, memory = 384, gpu = 0 },
    "r5.16xlarge"   = { cpu = 64, memory = 512, gpu = 0 },
    "r5.24xlarge"   = { cpu = 96, memory = 768, gpu = 0 },
    "r5.metal"      = { cpu = 96, memory = 768, gpu = 0 },
    "r5a.large"     = { cpu = 2, memory = 16, gpu = 0 },
    "r5a.xlarge"    = { cpu = 4, memory = 32, gpu = 0 },
    "r5a.2xlarge"   = { cpu = 8, memory = 64, gpu = 0 },
    "r5a.4xlarge"   = { cpu = 16, memory = 128, gpu = 0 },
    "r5a.8xlarge"   = { cpu = 32, memory = 256, gpu = 0 },
    "r5a.12xlarge"  = { cpu = 48, memory = 384, gpu = 0 },
    "r5a.16xlarge"  = { cpu = 64, memory = 512, gpu = 0 },
    "r5a.24xlarge"  = { cpu = 96, memory = 768, gpu = 0 },
    "r5ad.large"    = { cpu = 2, memory = 16, gpu = 0 },
    "r5ad.xlarge"   = { cpu = 4, memory = 32, gpu = 0 },
    "r5ad.2xlarge"  = { cpu = 8, memory = 64, gpu = 0 },
    "r5ad.4xlarge"  = { cpu = 16, memory = 128, gpu = 0 },
    "r5ad.12xlarge" = { cpu = 48, memory = 384, gpu = 0 },
    "r5ad.24xlarge" = { cpu = 96, memory = 768, gpu = 0 },
    "r5d.large"     = { cpu = 2, memory = 16, gpu = 0 },
    "r5d.xlarge"    = { cpu = 4, memory = 32, gpu = 0 },
    "r5d.2xlarge"   = { cpu = 8, memory = 64, gpu = 0 },
    "r5d.4xlarge"   = { cpu = 16, memory = 128, gpu = 0 },
    "r5d.8xlarge"   = { cpu = 32, memory = 256, gpu = 0 },
    "r5d.12xlarge"  = { cpu = 48, memory = 384, gpu = 0 },
    "r5d.16xlarge"  = { cpu = 64, memory = 512, gpu = 0 },
    "r5d.24xlarge"  = { cpu = 96, memory = 768, gpu = 0 },
    "r5d.metal"     = { cpu = 96, memory = 768, gpu = 0 },
    "r4.large"      = { cpu = 2, memory = 15.25, gpu = 0 },
    "r4.xlarge"     = { cpu = 4, memory = 30.5, gpu = 0 },
    "r4.2xlarge"    = { cpu = 8, memory = 61, gpu = 0 },
    "r4.4xlarge"    = { cpu = 16, memory = 122, gpu = 0 },
    "r4.8xlarge"    = { cpu = 32, memory = 244, gpu = 0 },
    "r4.16xlarge"   = { cpu = 64, memory = 488, gpu = 0 },
    "i3.large"      = { cpu = 2, memory = 15.25, gpu = 0 },
    "i3.xlarge"     = { cpu = 4, memory = 30.5, gpu = 0 },
    "i3.2xlarge"    = { cpu = 8, memory = 61, gpu = 0 },
    "i3.4xlarge"    = { cpu = 16, memory = 122, gpu = 0 },
    "i3.8xlarge"    = { cpu = 32, memory = 244, gpu = 0 },
    "i3.16xlarge"   = { cpu = 64, memory = 488, gpu = 0 },
    "i3.metal"      = { cpu = 72, memory = 512, gpu = 0 },
    "i3en.large"    = { cpu = 2, memory = 16, gpu = 0 },
    "i3en.xlarge"   = { cpu = 4, memory = 32, gpu = 0 },
    "i3en.2xlarge"  = { cpu = 8, memory = 64, gpu = 0 },
    "i3en.3xlarge"  = { cpu = 12, memory = 96, gpu = 0 },
    "i3en.6xlarge"  = { cpu = 24, memory = 192, gpu = 0 },
    "i3en.12xlarge" = { cpu = 48, memory = 384, gpu = 0 },
    "i3en.24xlarge" = { cpu = 96, memory = 768, gpu = 0 },
    "i3en.metal"    = { cpu = 96, memory = 768, gpu = 0 },
    "h1.2xlarge"    = { cpu = 8, memory = 32, gpu = 0 },
    "h1.4xlarge"    = { cpu = 16, memory = 64, gpu = 0 },
    "h1.8xlarge"    = { cpu = 32, memory = 128, gpu = 0 },
    "h1.16xlarge"   = { cpu = 64, memory = 256, gpu = 0 },
    "d2.xlarge"     = { cpu = 4, memory = 30.5, gpu = 0 },
    "d2.2xlarge"    = { cpu = 8, memory = 61, gpu = 0 },
    "d2.4xlarge"    = { cpu = 16, memory = 122, gpu = 0 },
    "d2.8xlarge"    = { cpu = 36, memory = 244, gpu = 0 }
  }

  gpu_ami_id_by_region = {
    eu-north-1     = "ami-0641def7f02a4cac5"
    eu-west-1      = "ami-0f9571a3e65dc4e20"
    eu-west-2      = "ami-032348bd69c5dd665"
    eu-west-3      = "ami-053962359d6859fec"
    eu-central-1   = "ami-0fbbd205f797ecccd"
    ap-southeast-1 = "ami-0a2f4c3aeb596aa7e"
    ap-southeast-2 = "ami-0a2f4c3aeb596aa7e"
    ap-northeast-1 = "ami-04cf69bbd6c0fae0b"
    ap-northeast-2 = "ami-0730e699ed0118737"
    ap-south-1     = "ami-005b754faac73f0cc"
    us-east-1      = "ami-0017d945a10387606"
    us-east-2      = "ami-0ccac9d9b57864000"
    us-west-2      = "ami-08335952e837d087b"
  }

}

# the commented out worker group list below shows an example of how to define
# multiple worker groups of differing configurations
# worker_groups = [
#   {
#     asg_desired_capacity = 2
#     asg_max_size = 10
#     asg_min_size = 2
#     instance_type = "m4.xlarge"
#     name = "worker_group_a"
#     additional_userdata = "echo foo bar"
#     subnets = "${join(",", module.vpc.private_subnets)}"
#   },
#   {
#     asg_desired_capacity = 1
#     asg_max_size = 5
#     asg_min_size = 1
#     instance_type = "m4.2xlarge"
#     name = "worker_group_b"
#     additional_userdata = "echo foo bar"
#     subnets = "${join(",", module.vpc.private_subnets)}"
#   },
# ]

# the commented out worker group tags below shows an example of how to define
# custom tags for the worker groups ASG
# worker_group_tags = {
#   worker_group_a = [
#     {
#       key                 = "k8s.io/cluster-autoscaler/node-template/taint/nvidia.com/gpu"
#       value               = "gpu:NoSchedule"
#       propagate_at_launch = true
#     },
#   ],
#   worker_group_b = [
#     {
#       key                 = "k8s.io/cluster-autoscaler/node-template/taint/nvidia.com/gpu"
#       value               = "gpu:NoSchedule"
#       propagate_at_launch = true
#     },
#   ],
# }
#  worker_groups_launch_template = [
#    {
#      # This will launch an autoscaling group with only Spot Fleet instances
#      instance_type                            = "${var.spot_fleet_instance_type}"
#      subnets                                  = "${join(",", module.vpc.private_subnets)}"
#      additional_security_group_ids            = "${module.security_groups.worker_group_one_id},${module.security_groups.worker_group_two_id}"
#      asg_desired_capacity                     = "${var.spot_fleet_asg_desired_capacity}"
#      spot_instance_pools                      = 10
#      on_demand_percentage_above_base_capacity = "0"
#    },
#  ]

