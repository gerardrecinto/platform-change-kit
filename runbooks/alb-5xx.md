# Alarm: target 5xx

Fires when the app returns more than the threshold of 5xx responses per minute for 3 of 5 minutes.

1. Did a deploy just happen? `aws ecs describe-services --cluster <name> --services <name> --query 'services[0].deployments'`. If a deployment is still rolling, the circuit breaker is already deciding. Watch it for 5 minutes before touching anything.
2. If the 5xx started with the deploy and the breaker has not rolled back, roll back by hand: point the service at the previous task definition revision (`aws ecs update-service --task-definition <family>:<previous>`).
3. No deploy? Look at the logs: `aws logs tail /ecs/<name> --since 15m --filter-pattern '"ERROR"'`.
4. Check a dependency (database, third-party API). A 5xx with healthy tasks usually means the app is failing behind the health check.
5. Post in the incident channel: what you saw, what you did, who has it.

Done when the alarm is OK for 15 minutes. Write down the cause before closing.
