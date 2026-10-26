#!/usr/bin/env python3
"""Install Codex skills and roles into an existing project, without cloning it."""

import argparse
import io
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ARCHIVE_URL = "https://codeload.github.com/maxpawgdbs/codex-agents/zip/refs/heads/main"
IGNORE_START = "# >>> codex-agents >>>"
IGNORE_END = "# <<< codex-agents <<<"


def destination(relative):
    """Select only the kit's capabilities, preserving paths within each skill."""
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError(f"Unsafe source path: {relative}")
    parts = path.parts
    if parts[:2] == (".agents", "skills") and len(parts) >= 4:
        return path.as_posix()
    if parts[:4] == ("plugins", "session-tools", "skills", "session-handoff") and len(parts) >= 5:
        return PurePosixPath(".agents", "skills", *parts[3:]).as_posix()
    if parts[:2] == (".codex", "agents") and len(parts) == 3 and path.suffix == ".toml":
        return path.as_posix()
    return None


def collect_files(source=None):
    files = {}

    def add(relative, data):
        target = destination(relative)
        if target:
            if target in files:
                raise ValueError(f"Duplicate capability path: {target}")
            files[target] = data

    if source is not None:
        for folder in [source / ".agents/skills", source / ".codex/agents",
                       source / "plugins/session-tools/skills/session-handoff"]:
            for path in sorted(folder.rglob("*")):
                if path.is_symlink():
                    raise ValueError(f"Symlink in source: {path}")
                if path.is_file():
                    add(path.relative_to(source).as_posix(), path.read_bytes())
    else:
        request = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "codex-agents-installer"})
        with urllib.request.urlopen(request, timeout=60) as response:
            archive_data = response.read()
        with zipfile.ZipFile(io.BytesIO(archive_data)) as archive:
            for info in archive.infolist():
                if not info.is_dir():
                    parts = info.filename.split("/", 1)
                    if len(parts) == 2 and destination(parts[1]):
                        if (info.external_attr >> 16) & 0o170000 == 0o120000:
                            raise ValueError(f"Symlink in archive: {info.filename}")
                        add(parts[1], archive.read(info))
    if not any(path.endswith("/SKILL.md") for path in files):
        raise ValueError("No skills found; check the source or repository access")
    return files


def safe_target(root, relative):
    path = root
    parts = PurePosixPath(relative).parts
    if not parts or PurePosixPath(relative).is_absolute() or ".." in parts or "\\" in relative:
        raise ValueError(f"Unsafe destination: {relative}")
    for index, part in enumerate(parts):
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Destination is a symlink: {path}")
        if index < len(parts) - 1 and path.exists() and not path.is_dir():
            raise ValueError(f"Destination parent is not a directory: {path}")
    return path


def ignore_contents(original, files):
    entries = set()
    for relative in files:
        parts = PurePosixPath(relative).parts
        if parts[:2] == (".agents", "skills"):
            entries.add("/" + "/".join(parts[:3]) + "/")
        else:
            entries.add("/" + relative)
    newline = "\r\n" if "\r\n" in original else "\n"
    block = newline.join([IGNORE_START, *sorted(entries), IGNORE_END]) + newline
    lines = original.splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == IGNORE_START]
    ends = [index for index, line in enumerate(lines) if line.rstrip("\r\n") == IGNORE_END]
    if not starts and not ends:
        separator = "" if not original or original.endswith(("\n", "\r")) else newline
        return original + separator + block
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError("Malformed codex-agents block in .gitignore; fix it before installing")
    return "".join(lines[:starts[0]]) + block + "".join(lines[ends[0] + 1:])


def install(root, files):
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Target project does not exist: {root}")
    pending = []
    # Check every collision and the ignore block before modifying the project.
    for relative, data in sorted(files.items()):
        path = safe_target(root, relative)
        if path.exists():
            if not path.is_file() or path.read_bytes() != data:
                raise ValueError(f"Existing file differs; no changes made: {path}")
        else:
            pending.append((path, data))
    ignore = safe_target(root, ".gitignore")
    original = ignore.read_bytes().decode("utf-8") if ignore.exists() else ""
    updated = ignore_contents(original, files)
    for path, data in pending:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if updated != original:
        ignore.write_bytes(updated.encode("utf-8"))
    return len(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="existing project; default: current directory")
    parser.add_argument("--source", type=Path, help="local kit checkout instead of downloading GitHub main")
    args = parser.parse_args()
    try:
        files = collect_files(args.source.resolve() if args.source else None)
        count = install(args.target, files)
    except (OSError, ValueError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    skills = sum(path.endswith("/SKILL.md") for path in files)
    roles = sum(path.startswith(".codex/agents/") for path in files)
    print(f"Ready: {skills} skills, {roles} roles; {count} new files.")
    print(f"Updated .gitignore in {args.target.resolve()}. Run codex in this project.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
