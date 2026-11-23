"""Change plans: small steps, each with a check and a way back.

A plan is a TOML file. The validator rejects the shapes that cause bad nights:
a big-bang step, no rollback, production before staging, no announcement.
"""

import tomllib
from dataclasses import dataclass

ENV_ORDER = ["dev", "staging", "prod"]
MAX_RESOURCES = 5
REQUIRED_STEP_FIELDS = ["id", "env", "summary", "apply", "validate", "rollback"]


@dataclass
class Issue:
    level: str  # "error" or "warning"
    where: str
    message: str

    def __str__(self):
        return f"{self.level.upper():7} {self.where}: {self.message}"


def load(path):
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def validate(plan):
    issues = []
    change = plan.get("change", {})
    steps = plan.get("step", [])
    order = change.get("env_order", ENV_ORDER)
    limit = change.get("max_resources", MAX_RESOURCES)

    for field in ("title", "owner"):
        if not change.get(field):
            issues.append(Issue("error", "change", f"missing {field}"))
    if not change.get("notify"):
        issues.append(Issue("error", "change", "notify list is empty: say who hears about this before work starts"))
    if int(change.get("announce_hours_before", 0)) < 1:
        issues.append(Issue("error", "change", "announce_hours_before must be at least 1"))
    if not steps:
        issues.append(Issue("error", "change", "no steps"))

    seen_ids = set()
    seen_envs = []
    last_index = -1
    for i, step in enumerate(steps, 1):
        where = f"step {step.get('id', i)}"
        for field in REQUIRED_STEP_FIELDS:
            if not str(step.get(field, "")).strip():
                issues.append(Issue("error", where, f"missing {field}"))
        sid = step.get("id")
        if sid in seen_ids:
            issues.append(Issue("error", where, "duplicate step id"))
        seen_ids.add(sid)

        env = step.get("env")
        if env not in order:
            issues.append(Issue("error", where, f"unknown environment {env!r}, expected one of {order}"))
            continue
        index = order.index(env)
        if index < last_index:
            issues.append(Issue("error", where, f"{env} comes after a later environment: order steps {' > '.join(order)}"))
        last_index = max(last_index, index)
        if env == order[-1] and any(e not in seen_envs for e in order[:-1]):
            missing = [e for e in order[:-1] if e not in seen_envs]
            issues.append(Issue("error", where, f"{env} step with no earlier step in {', '.join(missing)}"))
        seen_envs.append(env)

        resources = step.get("resources", [])
        if len(resources) > limit:
            issues.append(Issue("error", where, f"touches {len(resources)} resources, limit is {limit}: split it"))
        if not resources:
            issues.append(Issue("warning", where, "no resources listed, blast radius unknown"))

        rollback = str(step.get("rollback", "")).strip().lower()
        if rollback == "none" and not step.get("irreversible"):
            issues.append(Issue("error", where, "rollback is none but the step is not marked irreversible"))
        if step.get("irreversible") and not step.get("approved_by"):
            issues.append(Issue("error", where, "irreversible step needs approved_by"))
        if env == order[-1] and not step.get("soak_minutes"):
            issues.append(Issue("warning", where, f"no soak_minutes: say how long to watch {env} before moving on"))
    return issues


def has_errors(issues):
    return any(i.level == "error" for i in issues)
