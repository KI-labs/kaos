variable "tags" {
  type = "map"

  default = {
    project = "kaos"
    env     = "test"
    version = "2"
  }
}

variable "region" {
  default = "us-west-1"
}

variable main_cidr {
  type    = "string"
  default = "10.0.0.0/16"
}

variable "on_demand_instance_type" {
  default = "t2.small"
}

variable "on_demand_asg_desired_capacity" {
  default = 1
}

variable "spot_fleet_instance_type" {
  default = "t2.small"
}

variable "spot_fleet_asg_desired_capacity" {
  default = 1
}
