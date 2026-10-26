---
name: coordinate-work
description: "Coordinate explicitly requested multi-agent work with bounded tasks, clear file ownership, and concise evidence-based handoffs."
---

# Coordinate work

Delegate only work whose independent result will help the parent make progress. Keep tightly coupled changes in one context. Respect the environment's available tools, limits, and authorization.

- Define the shared goal and acceptance criteria, then identify independent questions or file boundaries.
- Give each worker a compact contract: objective, relevant paths, ownership, dependencies, expected result, and verification. Include necessary constraints without copying the entire conversation.
- Prefer the native `scout`, `implementer`, and `reviewer` roles where available. In a shared checkout, assign non-overlapping writable files; use separate worktrees when overlap is required.
- Keep integration decisions with the parent. Workers return evidence and results; the parent resolves conflicts and verifies the combined behavior.
- Reuse an existing worker for a related follow-up when useful. Avoid recursively spawning teams, duplicate exploration, and polling without a state change.
- Track actual agent IDs, parent relationships, task, ownership, status, and next dependency. Never infer that an agent is running from an old status message.

Return the integrated outcome, verification, and unresolved dependencies. An optional status table or Mermaid graph may summarize observed relationships. A diagram is a snapshot, not live telemetry. If delegation tools are unavailable, perform the work sequentially and say so.
