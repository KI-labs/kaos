output "worker_additional_policies" {
  value = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    aws_iam_policy.cluster_autoscaler.arn,
  ]
}

