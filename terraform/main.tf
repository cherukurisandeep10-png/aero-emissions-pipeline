provider "aws" {
  region = var.aws_region
}

# 1. S3 Bucket acting as Cloud Data Lake (Bronze & Silver Zones)
resource "aws_s3_bucket" "lakehouse_bucket" {
  bucket        = var.bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "lakehouse_bucket_privacy" {
  bucket = aws_s3_bucket.lakehouse_bucket.id

  block_public_accls_true = true
  block_public_policy     = true
  ignore_public_accls     = true
  restrict_public_buckets = true
}

# 2. Glue Database for Metadata Schema definition
resource "aws_glue_catalog_database" "aerostream_db" {
  name = "aerostream_lakehouse_db"
}

# 3. Glue Crawler to automatically catalog Bronze Parquet partitions
resource "aws_glue_crawler" "aerostream_crawler" {
  database_name = aws_glue_catalog_database.aerostream_db.name
  name          = "aerostream_bronze_crawler"
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.lakehouse_bucket.bucket}/bronze/flights/"
  }
}

# 4. IAM Role for Glue crawler access
resource "aws_iam_role" "glue_role" {
  name = "aerostream-glue-crawler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Custom S3 access policy for Glue role
resource "aws_iam_policy" "glue_s3_policy" {
  name        = "aerostream-glue-s3-access"
  description = "Allows AWS Glue crawler to read data from AeroStream S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:aws:s3:::${var.bucket_name}",
          "arn:aws:aws:s3:::${var.bucket_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_s3_attach" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.glue_s3_policy.arn
}
