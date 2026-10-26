#!/usr/bin/env python3
"""Validate this repository's deliberately small skill/package conventions."""

import json
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def read_skill(path):
    """Parse the documented two-scalar YAML subset, not arbitrary YAML."""
    text = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"---\n(.*?)\n---\n(.+)", text, re.DOTALL)
    if not match or not match[2].strip():
        raise ValueError(f"{path}: expected frontmatter and nonempty instructions")
    metadata = {}
    for line in match[1].splitlines():
        key, separator, value = line.partition(": ")
        if not separator or key not in {"name", "description"} or key in metadata:
            raise ValueError(f"{path}: use unique name and description fields")
        metadata[key] = json.loads(value) if key == "description" else value
    name = metadata.get("name", "")
    description = metadata.get("description")
    if not NAME.fullmatch(name) or len(name) > 64 or name != path.parent.name:
        raise ValueError(f"{path}: invalid or mismatched skill name")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"{path}: description must be a nonempty quoted string")
    if len(description) > 1024 or "<" in description or ">" in description:
        raise ValueError(f"{path}: invalid description")
    return metadata


def local_path(root, value):
    if not isinstance(value, str) or not value.startswith("./"):
        raise ValueError(f"expected a ./-prefixed local path: {value!r}")
    if ".." in PurePosixPath(value).parts or "\\" in value:
        raise ValueError(f"path must stay inside its package: {value!r}")
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()) or not target.exists():
        raise ValueError(f"missing or escaping local path: {value!r}")
    return target


def check(root):
    required = ["README.md", "AGENTS.md", ".codex/config.toml",
                ".agents/plugins/marketplace.json", "catalog/tools.json",
                "docs/tools.md", "docs/selection.md", "evals/README.md"]
    for relative in required:
        if not (root / relative).is_file():
            raise ValueError(f"missing required file: {relative}")
    for pattern, loader in [("*.json", json.loads), ("*.toml", tomllib.loads)]:
        for path in root.rglob(pattern):
            if not {".git", ".venv", "node_modules", "runs"}.intersection(path.relative_to(root).parts):
                loader(path.read_text(encoding="utf-8"))

    skills = list((root / ".agents/skills").glob("*/SKILL.md"))
    marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    if not NAME.fullmatch(marketplace["name"]):
        raise ValueError("invalid marketplace name")
    plugins = {}
    for entry in marketplace["plugins"]:
        if entry["name"] in plugins or entry["source"]["source"] != "local":
            raise ValueError("expected unique, local marketplace entries")
        plugin_root = local_path(root, entry["source"]["path"])
        manifest = json.loads((plugin_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        if manifest["name"] != entry["name"] or not NAME.fullmatch(manifest["name"]):
            raise ValueError("plugin manifest and marketplace names must match")
        if not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
            raise ValueError("plugin requires a three-part version")
        if not manifest["description"] or not manifest["interface"]["displayName"]:
            raise ValueError("plugin requires description and interface.displayName")
        if entry["policy"]["installation"] not in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}:
            raise ValueError("invalid installation policy")
        if entry["policy"]["authentication"] not in {"ON_INSTALL", "ON_USE"} or not entry["category"]:
            raise ValueError("invalid authentication policy or category")
        skill_root = local_path(plugin_root, manifest["skills"])
        packaged_skills = list(skill_root.glob("*/SKILL.md"))
        if not packaged_skills:
            raise ValueError("plugin skill directory is empty")
        skills.extend(packaged_skills)
        plugins[f'{entry["name"]}@{marketplace["name"]}'] = entry

    names = set()
    for path in skills:
        metadata = read_skill(path)
        if metadata["name"] in names:
            raise ValueError(f'duplicate skill: {metadata["name"]}')
        names.add(metadata["name"])

    config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
    for key, settings in config.get("plugins", {}).items():
        if key not in plugins or not isinstance(settings.get("enabled"), bool):
            raise ValueError(f"invalid configured plugin: {key}")
    roles = set()
    for path in (root / ".codex/agents").glob("*.toml"):
        role = tomllib.loads(path.read_text(encoding="utf-8"))
        if role["name"] != path.stem or role["name"] in roles:
            raise ValueError(f"invalid or duplicate role name: {path}")
        if not role["description"].strip() or not role["developer_instructions"].strip():
            raise ValueError(f"empty role instructions: {path}")
        roles.add(role["name"])

    print(f"OK: {len(skills)} skills, {len(roles)} roles, {len(plugins)} local plugin.")
    print("Skill discovery descriptions (characters; not a token estimate):")
    for path in sorted(skills):
        metadata = read_skill(path)
        print(f'  {metadata["name"]}: {len(metadata["description"])}')


if __name__ == "__main__":
    try:
        check(ROOT)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
