terraform {
  required_version = ">= 1.5.0"
  backend "s3" {
    bucket = "example-tfstate"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

variable "environment" {
  type    = string
  default = "prod"
}

module "vpc" {
  source = "./modules/vpc"
}

resource "aws_instance" "web" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
}

resource "aws_instance" "worker" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.small"
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "example-artifacts"
}

output "web_ip" {
  value = aws_instance.web.public_ip
}
