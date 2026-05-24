output "s3_bucket_arn" {
  description = "The ARN of the Data Lake S3 Bucket."
  value       = aws_s3_bucket.lakehouse_bucket.arn
}

output "glue_database_name" {
  description = "The AWS Glue database catalog name."
  value       = aws_glue_catalog_database.aerostream_db.name
}

output "glue_crawler_name" {
  description = "The AWS Glue Crawler name for Parquet schema discovery."
  value       = aws_glue_crawler.aerostream_crawler.name
}
