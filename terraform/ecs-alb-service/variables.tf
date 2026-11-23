variable "name" {
  description = "Name prefix for every resource."
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  description = "Subnets for the load balancer. At least two, in different zones."
  type        = list(string)
  validation {
    condition     = length(var.public_subnet_ids) >= 2
    error_message = "Use at least two public subnets so the load balancer spans two zones."
  }
}

variable "private_subnet_ids" {
  description = "Subnets for the tasks. At least two, in different zones."
  type        = list(string)
  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "Use at least two private subnets so tasks spread across two zones."
  }
}

variable "certificate_arn" {
  description = "ACM certificate for the HTTPS listener."
  type        = string
}

variable "container_image" {
  description = "Image to run. Pin a tag or digest, not latest."
  type        = string
  validation {
    condition     = !endswith(var.container_image, ":latest")
    error_message = "Pin the image to a tag or digest, not latest."
  }
}

variable "container_port" {
  type    = number
  default = 8080
}

variable "health_check_path" {
  type    = string
  default = "/healthz"
}

variable "desired_count" {
  description = "Tasks to run. Two or more so a deploy never takes the service to zero."
  type        = number
  default     = 2
  validation {
    condition     = var.desired_count >= 2
    error_message = "Run at least two tasks."
  }
}

variable "cpu" {
  type    = number
  default = 256
}

variable "memory" {
  type    = number
  default = 512
}

variable "environment" {
  description = "Plain environment variables for the container. Put secrets in Secrets Manager, not here."
  type        = map(string)
  default     = {}
}

variable "ingress_cidrs" {
  description = "Who can reach the load balancer."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ssl_policy" {
  description = "TLS policy for the HTTPS listener."
  type        = string
  default     = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}

variable "idle_timeout" {
  description = "Seconds before the load balancer closes an idle connection."
  type        = number
  default     = 60
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "access_log_bucket" {
  description = "S3 bucket for load balancer access logs. Empty turns them off."
  type        = string
  default     = ""
}

variable "log_retention_days" {
  type    = number
  default = 90
}

variable "log_kms_key_arn" {
  description = "KMS key for the container log group. Empty uses the default."
  type        = string
  default     = null
}

variable "alarm_actions" {
  description = "SNS topic ARNs to notify when an alarm fires."
  type        = list(string)
  default     = []
}

variable "alarm_5xx_threshold" {
  description = "Target 5xx responses per minute that raise the alarm."
  type        = number
  default     = 5
}

variable "tags" {
  type    = map(string)
  default = {}
}
