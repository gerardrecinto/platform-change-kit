# Rolling back a change

Use the change plan. Every step has a rollback written before work started.

1. Stop. Do not apply the next step.
2. Run the rollback of the failed step, then every earlier step in reverse order. `pck simulate <plan> --fail-at <step-id>` prints that order.
3. Run each step's check again to prove it is back.
4. Post the result where the announcement went. Say what failed and what is next.
5. Do not retry the same plan unchanged. Fix the cause or shrink the step first.

Service deploys: the ECS circuit breaker rolls back a service whose new tasks keep failing. It does not catch a deploy that is healthy but wrong. For that, use the check in the plan and the 5xx alarm.
