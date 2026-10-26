---
name: review-changes
description: "Review a specified diff or uncommitted changes for actionable correctness, security, and compatibility defects."
---

# Review changes

Resolve the requested base and scope before reviewing. If no base is supplied, inspect staged and unstaged changes plus relevant untracked files; do not silently assume `HEAD~1`.

- Read the diff, affected contracts, and relevant callers. Focus on defects introduced by the change.
- Check error handling, boundaries, state transitions, and compatibility when the patch touches them.
- Validate suspicious behavior with a targeted check when feasible. Label unresolved hypotheses.
- Report each actionable finding with severity, a precise location, the triggering case, and impact. Deduplicate symptoms of the same cause.
- Exclude preferences and unrelated pre-existing issues from defect findings.

Do not edit files unless requested. Lead with findings; if none remain, say so and state material verification gaps. Avoid repeating the patch in the report.
