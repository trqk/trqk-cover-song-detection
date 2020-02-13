terraform {
  backend "s3" {
    bucket = "trqk-terraform-backend"
    key    = "trqk-client-web.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "trqk-terraform-backend"
  }
}

provider "aws" {
  version = "~> 2.0"
  region = "us-east-1"
}


resource "aws_iam_group" "manage-integrations-lite-staticfiles-s3-bucket" {
  name = "Manage-Integrations-Lite-static-files"
}

resource "aws_iam_user" "manage-integrations-lite-staticfiles-s3-bucket" {
  name = "Manage-Integrations-Lite-static-files"
}

resource "aws_iam_group_membership" "manage-integrations-lite-staticfiles-s3-bucket" {
  group = "${aws_iam_group.manage-integrations-lite-staticfiles-s3-bucket.name}"
  name = "Manage-Integrations-Lite-static-files"
  users = ["${aws_iam_user.manage-integrations-lite-staticfiles-s3-bucket.name}"]
}

resource "aws_iam_group_policy" "manage-integrations-lite-staticfiles-s3-bucket" {
  group = "${aws_iam_group.manage-integrations-lite-staticfiles-s3-bucket.name}"
  policy =<<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ManageIntegrationsLiteStaticfilesBucket",
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": [
          "arn:aws:s3:::integrations-lite-staticfiles",
          "arn:aws:s3:::integrations-lite-staticfiles/*"
      ]
    }
  ]
}
POLICY
}

resource "aws_s3_bucket" "integrations-lite-staticfiles-s3-bucket" {
  region = "${var.region}"
  bucket = "integrations-lite-staticfiles"
  acl = "public-read"
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers = ["ETag"]
    max_age_seconds = 3000
  }
  website {
    index_document = "index.html"
  }
  policy =<<POLICY
{
  "Version":"2012-10-17",
  "Statement":[{
    "Sid":"PublicReadGetObject",
    "Effect":"Allow",
    "Principal": "*",
    "Action":["s3:GetObject"],
    "Resource":[
      "arn:aws:s3:::integrations-lite-staticfiles",
      "arn:aws:s3:::integrations-lite-staticfiles/*"
    ]
  }]
}
POLICY
}
