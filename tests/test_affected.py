import os
import tempfile
import unittest

from pck import affected as aff

ROOT = os.path.join(os.path.dirname(__file__), "..", "examples", "monorepo")


class AffectedTests(unittest.TestCase):
    def setUp(self):
        self.projects = aff.load_projects(ROOT)
        self.globals = aff.load_global_paths(ROOT)

    def run_for(self, *files):
        return aff.affected(self.projects, files, self.globals)

    def test_leaf_change_builds_only_the_leaf(self):
        self.assertEqual(self.run_for("services/worker/jobs.py")["affected"], ["worker"])

    def test_shared_library_change_builds_dependents_in_order(self):
        result = self.run_for("libs/db/pool.py")
        self.assertEqual(result["affected"], ["db", "api", "worker"])
        self.assertEqual(result["reasons"]["api"], ["depends on db"])

    def test_root_library_reaches_everything_that_uses_it(self):
        self.assertEqual(
            self.run_for("libs/common/logging.py")["affected"],
            ["common", "db", "api", "web", "worker"],
        )

    def test_leading_dot_slash_is_ignored_but_dot_directories_are_kept(self):
        self.assertEqual(self.run_for("./services/worker/jobs.py")["affected"], ["worker"])
        self.assertTrue(self.run_for("./.github/ci.yml")["everything"])

    def test_extra_path_triggers_two_projects(self):
        self.assertEqual(self.run_for("schemas/openapi.yaml")["affected"], ["api", "web"])

    def test_global_file_rebuilds_everything(self):
        result = self.run_for(".github/ci.yml")
        self.assertTrue(result["everything"])
        self.assertEqual(len(result["affected"]), len(self.projects))

    def test_docs_only_change_builds_nothing(self):
        result = self.run_for("README.md")
        self.assertEqual(result["affected"], [])
        self.assertEqual(result["unowned"], ["README.md"])

    def test_matrix_shape(self):
        m = aff.matrix(self.projects, self.run_for("libs/db/pool.py"))
        self.assertEqual([i["project"] for i in m["include"]], ["db", "api", "worker"])
        self.assertEqual(m["include"][1]["path"], "services/api")

    def test_cycle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, dep in (("a", "b"), ("b", "a")):
                os.makedirs(os.path.join(tmp, name))
                with open(os.path.join(tmp, name, "project.json"), "w") as fh:
                    fh.write('{"name": "%s", "depends_on": ["%s"]}' % (name, dep))
            with self.assertRaises(ValueError):
                aff.load_projects(tmp)

    def test_unknown_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "a"))
            with open(os.path.join(tmp, "a", "project.json"), "w") as fh:
                fh.write('{"name": "a", "depends_on": ["ghost"]}')
            with self.assertRaises(ValueError):
                aff.load_projects(tmp)


if __name__ == "__main__":
    unittest.main()
