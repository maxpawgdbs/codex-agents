---
name: session-handoff
description: "Create a compact continuation brief when the user asks to hand off, resume elsewhere, or summarize a long-running task."
---

# Session handoff

Return a continuation brief containing:

- Goal, acceptance criteria, and current user constraints.
- Current branch or worktree, relevant changed paths, and unfinished work.
- Established decisions and evidence, including meaningful failed approaches to avoid repeating.
- Checks actually run with results, plus verification still needed.
- Active agent IDs, ownership, dependencies, and observed status if a team exists.
- The next concrete action and remaining blockers.

Use file paths and symbols instead of copying code, full logs, or conversation history. Separate observations from assumptions. Preserve material constraints even if the brief grows. Do not include credentials or fabricate hidden reasoning.

Produce the brief in the conversation. Write a file only if the user requests one. On resumption, verify current repository and agent state before relying on the brief.
