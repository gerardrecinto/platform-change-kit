# Using AI tools on platform work

Rules a small team can follow without a policy committee.

1. No secrets, tokens, customer data or health data in a prompt. Use fake values or a local model for anything sensitive.
2. AI-written infrastructure goes through the same gates as any other change: a plan with a check and a rollback, `terraform validate`, a plan review, and a second person for production.
3. The person who ships it owns it. If you cannot explain a line, do not merge it.
4. Prefer small, checkable asks (a runbook draft, a test, a refactor) over large generated rewrites.
5. Treat output as untrusted input: run the tests, read the diff, and watch for invented flags and resource names.
6. Keep prompts that work in the repo so others can reuse them.

`pck check` is the gate for rule 2: it rejects a change with no rollback or no earlier staging step, however it was written.
