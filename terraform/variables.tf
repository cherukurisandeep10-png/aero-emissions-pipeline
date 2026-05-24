variable "aws_region" {
  description = "The target AWS region to deploy infrastructure."
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Globally unique name for the S3 Data Lakehouse bucket."
  type        = string
  default     = "aerostream-aviation-lakehouse-dev"
}
