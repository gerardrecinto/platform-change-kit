"""Turn a plan into the two things people need: a runbook and a heads-up message."""


def render_runbook(plan):
    change = plan["change"]
    lines = [f"# {change['title']}", ""]
    lines.append(f"Owner: {change['owner']}")
    if change.get("window"):
        lines.append(f"Window: {change['window']}")
    lines.append(f"Announce {change['announce_hours_before']}h before to: {', '.join(change['notify'])}")
    lines += ["", "## Steps", ""]
    for n, step in enumerate(plan["step"], 1):
        lines.append(f"### {n}. {step['id']} ({step['env']})")
        lines.append("")
        lines.append(step["summary"])
        lines.append("")
        lines.append(f"- Touches: {', '.join(step.get('resources', [])) or 'not listed'}")
        lines.append(f"- Apply: `{step['apply']}`")
        lines.append(f"- Check: `{step['validate']}`")
        if step.get("expected"):
            lines.append(f"- Expect: {step['expected']}")
        if step.get("soak_minutes"):
            lines.append(f"- Watch for {step['soak_minutes']} minutes before the next step")
        lines.append(f"- Roll back: `{step['rollback']}`")
        lines.append("")
    lines += [
        "## If a check fails",
        "",
        "Stop. Run the rollback for the failed step, then for every earlier step in reverse order. "
        "Post the result in the channel above before trying again.",
        "",
    ]
    return "\n".join(lines)


def render_announcement(plan):
    change = plan["change"]
    envs = []
    for step in plan["step"]:
        if step["env"] not in envs:
            envs.append(step["env"])
    when = change.get("window") or "window to be confirmed"
    return (
        f"Heads-up: {change['title']}\n"
        f"Owner: {change['owner']}. When: {when}. "
        f"Order: {' then '.join(envs)}, {len(plan['step'])} steps, each checked before the next.\n"
        f"Every step has a rollback. If a check fails we stop and roll back, and I will post here.\n"
        f"Reply before the window if this clashes with something of yours."
    )
