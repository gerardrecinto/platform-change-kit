# platform-change-kit

Make platform changes small, checked and reversible.

- **Build less, trust it more.** `pck affected` picks the projects a change can break in a monorepo, in build order, and prints a GitHub Actions matrix.
- **Changes with a way back.** `pck check` rejects a change plan with no rollback, no announcement, a big-bang step, or production before staging. `pck runbook`, `pck announce` and `pck simulate` come from the same plan.
- **A service that heals a bad deploy.** A Terraform module for ECS Fargate behind an ALB: TLS 1.3 policy, private tasks, circuit-breaker rollback, alarms with runbooks.

Site and live demo: https://gerardrecinto.github.io/platform-change-kit/

## Try it

Python 3.11 or newer, standard library only.

```bash
git clone https://github.com/gerardrecinto/platform-change-kit && cd platform-change-kit

python3 -m pck affected --root examples/monorepo --changed libs/db/pool.py
python3 -m pck affected --root examples/monorepo --changed schemas/openapi.yaml --format matrix

python3 -m pck check examples/plans/https-only-listener.toml     # passes
python3 -m pck check examples/plans/big-bang.toml                # rejected, exit 1
python3 -m pck simulate examples/plans/https-only-listener.toml --fail-at staging-listener

python3 -m unittest discover -s tests -t .
```

Use it in a pull request job:

```yaml
- run: echo "matrix=$(python -m pck affected --root . --git-base origin/main --format matrix)" >> "$GITHUB_OUTPUT"
  id: pck
```

## The Terraform module

```bash
cd terraform/examples/dev
terraform init -backend=false && terraform validate
```

`terraform/ecs-alb-service` creates the load balancer (HTTPS on a TLS 1.3/1.2 policy, port 80 redirects, invalid headers dropped), a target group with health checks, an ECS cluster and service in private subnets, a log group, and three alarms. A deploy never drops below full capacity and a circuit breaker rolls back a deploy whose tasks keep failing. Image tags must be pinned and at least two tasks run.

## Layout

| Path | What |
|---|---|
| `pck/` | `affected`, `plan`, `runbook`, `simulate`, CLI |
| `examples/monorepo/` | six projects with dependencies, used by the tests and the site |
| `examples/plans/` | one plan that passes, one that is rejected |
| `terraform/ecs-alb-service/` | the module; `terraform/examples/dev` is the checked example |
| `runbooks/` | 5xx, unhealthy tasks, rolling back a change |
| `docs/` | the site, plus TLS and proxy choices, compliance notes, AI tool rules |

## Limits

The Terraform passes `fmt` and `validate` in CI. Commands inside plans are printed, never run. It is not certified for HIPAA, HITRUST or anything else; see `docs/controls.md` for what it could and could not show a compliance team.

MIT licensed.
