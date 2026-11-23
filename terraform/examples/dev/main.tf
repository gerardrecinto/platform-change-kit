# Example only. The IDs below are fake: this is checked with terraform validate, not applied.
provider "aws" {
  region = "us-west-2"
}

module "api" {
  source = "../../ecs-alb-service"

  name               = "api-dev"
  vpc_id             = "vpc-0123456789abcdef0"
  public_subnet_ids  = ["subnet-0aaa0aaa0aaa0aaa0", "subnet-0bbb0bbb0bbb0bbb0"]
  private_subnet_ids = ["subnet-0ccc0ccc0ccc0ccc0", "subnet-0ddd0ddd0ddd0ddd0"]
  certificate_arn    = "arn:aws:acm:us-west-2:111122223333:certificate/00000000-0000-0000-0000-000000000000"
  container_image    = "111122223333.dkr.ecr.us-west-2.amazonaws.com/api:1.4.2"

  environment         = { APP_ENV = "dev" }
  deletion_protection = false
}

output "url_target" {
  value = module.api.alb_dns_name
}
