---
name: verify-change
description: "Choose and run evidence-based validation when asked to check a patch, regression fix, or completion claim."
---

# Verify a change

Map each acceptance criterion and affected contract to an observable check.

- Discover existing commands in project instructions, manifests, and CI; reuse them rather than inventing a parallel suite.
- Start with the changed behavior and relevant tests. Include required repository checks.
- Broaden coverage when changes affect public APIs, shared state, security boundaries, migrations, or multiple consumers.
- For a bug fix, confirm the reproduction fails before the fix and passes after when practical; avoid disturbing concurrent work to do so.
- Capture command, exit status, and the relevant result. Save large output outside model context and inspect failing sections with enough surrounding detail.
- Repeat checks after a material change, a failure, or an unresolved concern. Once sufficient checks pass, finish the task.

Separate passed, failed, and unrun checks with reasons. Do not claim success from a command that was never executed or infer quality from a short diff alone.
