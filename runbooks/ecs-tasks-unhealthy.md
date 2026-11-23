# Alarm: unhealthy targets or running tasks low

Fires when a task fails its health check, or fewer tasks run than `desired_count`.

1. See why tasks stopped: `aws ecs describe-services --cluster <name> --services <name> --query 'services[0].events[:10]'`.
2. Look at the stopped reason: `aws ecs list-tasks --cluster <name> --desired-status STOPPED`, then `describe-tasks`. Common ones: `OutOfMemoryError` (raise memory), `Essential container exited` (read the logs), `CannotPullContainerError` (image tag or ECR permission).
3. Health check failing but the app looks fine? Compare `health_check_path` with what the app serves, and check the task security group allows the load balancer on the container port.
4. Capacity short of a zone? Confirm both private subnets have free IPs.
5. If a new revision is the cause, roll back (see `alb-5xx.md`, step 2).

Done when running tasks equals desired for 15 minutes.
