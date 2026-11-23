# Compliance notes (read this before quoting it)

This kit is a lab. It is not certified, audited or legal advice, and it has not handled real health data. What follows maps behavior in the code to the kind of safeguard a compliance team asks about, so you know what you could show them and what you could not.

| Safeguard a reviewer asks for | What this kit does | What it does not do |
|---|---|---|
| Encryption in transit | HTTPS listener with a TLS 1.3/1.2 policy, HTTP redirected | Encryption between load balancer and task |
| Encryption at rest | Optional KMS key for the log group | Databases and buckets, which are outside this module |
| Access control | Tasks in private subnets, reachable only from the load balancer; the app role starts with no permissions | Identity provider, user access reviews |
| Audit trail | Access logs to S3 when a bucket is set; container logs retained for 90 days by default | Log integrity, long retention rules |
| Change management | A plan needs an owner, an announcement, a check and a rollback per step, and production cannot come before staging | Approval workflows, ticket links |
| Availability | Two or more tasks across two zones, deploys that never drop below full capacity, circuit-breaker rollback | Disaster recovery across regions |

Questions to bring to the compliance team before building anything real: which data is in scope, what retention is required, whether traffic inside the VPC must be encrypted, who approves production changes, and what evidence they want kept.
