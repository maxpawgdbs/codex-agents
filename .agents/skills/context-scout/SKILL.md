---
name: context-scout
description: "Locate the minimal relevant code, contracts, and checks when starting an unfamiliar task or narrowing an oversized context."
---

# Context scout

Produce an evidence-backed map for the current question. Do not edit files unless separately requested.

- Start with applicable repository instructions, supplied paths, and the current diff.
- Search filenames with `rg --files`; search likely directories and symbols with `rg -n`.
- Read the relevant function, its callers, contracts, and nearby tests. Expand the search when these leave a material gap.
- Keep generated files, lockfiles, vendored code, and bulk logs out of the initial read unless the question concerns them.
- Preserve exact error messages and important edge cases; summarize repeated matches with paths instead of dumping them.
- Reuse established facts during the task; re-read when edits or new evidence may invalidate them.

Return relevant paths and symbols, the behavior they establish, useful check commands, and unresolved questions. Stop mapping once implementation can proceed; do not turn a small task into a repository audit.
