# Codex Agents

This repository contains reusable Codex skills, prompts, agent roles, and integration recipes.
User documentation and prompt examples are in Russian; executable identifiers are in English.

- Keep this file short. Put task-specific guidance in the matching skill or document.
- Skills live in `.agents/skills`; distributable plugin skills live in `plugins/`.
- Avoid overlapping triggers, mandatory workflows for trivial edits, and unconditional agent fanout.
- Prefer file paths and targeted searches to copying entire files or logs into context.
- Preserve user changes. Workers need separate file ownership or separate worktrees.
- Record observed actions, evidence, and short decision summaries; never fabricate internal reasoning or agent activity.
- New third-party recommendations need a primary source, compatibility notes, and a dated popularity snapshot.
- Treat token savings and quality gains as hypotheses until measured on comparable tasks.
- Run `python3 scripts/check.py` and `python3 -m unittest discover -s tests` after changing scripts or package structure.

Local convention: skill frontmatter has only a plain `name` and a single-line, JSON-quoted `description`. The checker validates this subset of YAML without dependencies.
