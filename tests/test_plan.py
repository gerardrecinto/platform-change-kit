import copy
import os
import unittest

from pck import plan as pl
from pck import runbook, simulate

PLANS = os.path.join(os.path.dirname(__file__), "..", "examples", "plans")


def good():
    return pl.load(os.path.join(PLANS, "https-only-listener.toml"))


def messages(issues, level="error"):
    return [i.message for i in issues if i.level == level]


class PlanTests(unittest.TestCase):
    def test_good_plan_has_no_errors(self):
        self.assertEqual(messages(pl.validate(good())), [])

    def test_big_bang_plan_is_rejected_for_the_right_reasons(self):
        issues = pl.validate(pl.load(os.path.join(PLANS, "big-bang.toml")))
        text = " | ".join(messages(issues))
        self.assertIn("touches 10 resources", text)
        self.assertIn("rollback is none", text)
        self.assertIn("no earlier step in dev, staging", text)
        self.assertIn("notify list is empty", text)

    def test_missing_rollback_is_an_error(self):
        plan = good()
        plan["step"][0]["rollback"] = ""
        self.assertIn("missing rollback", " ".join(messages(pl.validate(plan))))

    def test_prod_before_staging_is_an_error(self):
        plan = good()
        plan["step"] = [plan["step"][0], plan["step"][2]]
        self.assertIn("no earlier step in staging", " ".join(messages(pl.validate(plan))))

    def test_out_of_order_environments_are_an_error(self):
        plan = good()
        plan["step"].reverse()
        self.assertIn("comes after a later environment", " ".join(messages(pl.validate(plan))))

    def test_irreversible_step_needs_an_approver(self):
        plan = good()
        plan["step"][0]["rollback"] = "none"
        plan["step"][0]["irreversible"] = True
        self.assertIn("needs approved_by", " ".join(messages(pl.validate(plan))))
        plan["step"][0]["approved_by"] = "dana"
        self.assertEqual(messages(pl.validate(plan)), [])

    def test_prod_without_soak_is_a_warning_not_an_error(self):
        plan = copy.deepcopy(good())
        del plan["step"][2]["soak_minutes"]
        issues = pl.validate(plan)
        self.assertEqual(messages(issues), [])
        self.assertIn("no soak_minutes", " ".join(messages(issues, "warning")))


class RenderTests(unittest.TestCase):
    def test_runbook_lists_every_step_with_its_rollback(self):
        text = runbook.render_runbook(good())
        for step in good()["step"]:
            self.assertIn(step["id"], text)
            self.assertIn(step["rollback"], text)
        self.assertIn("Announce 24h before", text)

    def test_announcement_is_short_and_names_the_order(self):
        text = runbook.render_announcement(good())
        self.assertIn("dev then staging then prod", text)
        self.assertLessEqual(len(text.splitlines()), 4)

    def test_simulation_rolls_back_in_reverse_order(self):
        events, ok = simulate.simulate(good(), fail_at="staging-listener")
        self.assertFalse(ok)
        back = [e for e in events if e.startswith("rollback")]
        self.assertEqual([e.split()[1] for e in back], ["staging-listener", "dev-listener"])
        self.assertFalse(any("prod-listener" in e for e in events))

    def test_simulation_without_failure_applies_everything(self):
        events, ok = simulate.simulate(good())
        self.assertTrue(ok)
        self.assertEqual(len([e for e in events if e.startswith("apply")]), 3)


if __name__ == "__main__":
    unittest.main()
