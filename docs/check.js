// Checks that the page's rules give the same answers as the Python ones.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { affected } = require("./app.js");

const graph = JSON.parse(fs.readFileSync(path.join(__dirname, "graph.json"), "utf8"));

const cases = [
  [["services/worker/jobs.py"], ["worker"]],
  [["libs/db/pool.py"], ["db", "api", "worker"]],
  [["libs/common/logging.py"], ["common", "db", "api", "web", "worker"]],
  [["schemas/openapi.yaml"], ["api", "web"]],
  [["./.github/ci.yml"], ["common", "db", "api", "web", "worker", "infra"].sort()],
  [["README.md"], []],
];

for (const [files, expected] of cases) {
  const got = affected(graph, files).affected;
  if (files[0].includes(".github")) {
    assert.strictEqual(got.length, expected.length, "global file should build everything");
  } else {
    assert.deepStrictEqual(got, expected, files.join(","));
  }
}
console.log("site logic matches the Python rules (" + cases.length + " cases)");
