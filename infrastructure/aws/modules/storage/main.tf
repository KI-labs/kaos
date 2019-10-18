resource "aws_s3_bucket" "s3" {
  bucket = var.bucket_name
  region = var.region

  versioning {
    enabled = true
  }

  force_destroy = true

  tags = var.tags
}

