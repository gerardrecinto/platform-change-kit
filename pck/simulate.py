"""Dry-run a plan. Nothing is executed: this shows the order and what a failure undoes."""


def simulate(plan, fail_at=None):
    """Walk the steps. If fail_at names a step, its check fails and everything rolls back."""
    events = []
    done = []
    for step in plan["step"]:
        events.append(f"apply     {step['id']} ({step['env']}): {step['apply']}")
        done.append(step)
        events.append(f"check     {step['id']}: {step['validate']}")
        if step["id"] == fail_at:
            events.append(f"FAILED    {step['id']}: check did not pass, stopping")
            for back in reversed(done):
                events.append(f"rollback  {back['id']} ({back['env']}): {back['rollback']}")
            events.append("result    rolled back, nothing left half-applied")
            return events, False
        events.append(f"ok        {step['id']}")
    events.append("result    all steps applied and checked")
    return events, True
