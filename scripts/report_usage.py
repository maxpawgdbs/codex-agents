#!/usr/bin/env python3
"""Summarize completed Codex CLI JSONL turns; no network or model calls."""

import argparse
import json
import sys
from pathlib import Path


def read_usage(path):
    totals = dict(input_tokens=0, cached_input_tokens=0, output_tokens=0)
    turns = commands = 0
    pending_turn = False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("expected an event object")
            kind = event.get("type")
            if kind in {"turn.failed", "error"}:
                raise ValueError(f"run contains {kind}; not a successful comparison sample")
            if kind == "turn.started":
                pending_turn = True
            if kind == "item.completed" and event.get("item", {}).get("type") == "command_execution":
                commands += 1
            if kind != "turn.completed":
                continue
            usage = event["usage"]
            for key in totals:
                value = usage[key]
                if type(value) is not int or value < 0:
                    raise ValueError(f"invalid {key}")
            if usage["cached_input_tokens"] > usage["input_tokens"]:
                raise ValueError("cached input exceeds input")
            for key in totals:
                totals[key] += usage[key]
            turns += 1
            pending_turn = False
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise ValueError(f"{path}:{number}: {error}") from error
    if not turns or pending_turn:
        raise ValueError(f"{path}: missing completed usage or unfinished turn")
    return {"file": str(path), "turns": turns, "commands": commands, **totals,
            "uncached_input_tokens": totals["input_tokens"] - totals["cached_input_tokens"],
            "total_tokens": totals["input_tokens"] + totals["output_tokens"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", help="emit machine-readable rows")
    args = parser.parse_args()
    if len({path.resolve() for path in args.files}) != len(args.files):
        parser.error("the same run file was supplied more than once")
    try:
        rows = [read_usage(path) for path in args.files]
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print("| Run | Turns | Commands | Input | Cached input | Uncached input | Output | Total |")
        print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for row in rows:
            label = row["file"].replace("|", "\\|")
            values = [row[key] for key in ["turns", "commands", "input_tokens", "cached_input_tokens",
                                          "uncached_input_tokens", "output_tokens", "total_tokens"]]
            print("| " + " | ".join([label, *map(str, values)]) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
