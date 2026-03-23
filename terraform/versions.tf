terraform {
  required_version = ">= 1.8.0"

  required_providers {
    aws = {
      source  = "registry.opentofu.org/hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "oura-ring-poster-opentofu-state"
    key    = "oura-stats-texter/terraform.tfstate"
    region = "us-east-1"
  }
}
