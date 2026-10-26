import json
import tempfile
import unittest
from pathlib import Path

from scripts.report_usage import read_usage


def completed(input_tokens=100, cached_input_tokens=60, output_tokens=20):
    return {"type": "turn.completed", "usage": dict(input_tokens=input_tokens,
            cached_input_tokens=cached_input_tokens, output_tokens=output_tokens)}


class UsageTests(unittest.TestCase):
    def parse(self, events):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.jsonl"
            path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
            return read_usage(path)

    def test_cached_tokens_are_not_added_twice(self):
        result = self.parse([completed()])
        self.assertEqual(result["total_tokens"], 120)
        self.assertEqual(result["uncached_input_tokens"], 40)

    def test_sums_turns_and_counts_commands_once(self):
        command = {"type": "command_execution", "id": "item_1"}
        result = self.parse([{"type": "turn.started"}, {"type": "item.started", "item": command},
                             {"type": "item.completed", "item": command}, completed(),
                             {"type": "turn.started"}, completed(50, 10, 5)])
        self.assertEqual((result["turns"], result["commands"]), (2, 1))
        self.assertEqual(result["total_tokens"], 175)
        self.assertEqual(result["cached_input_tokens"], 70)

    def test_rejects_failed_run_with_earlier_success(self):
        with self.assertRaisesRegex(ValueError, "turn.failed"):
            self.parse([completed(), {"type": "turn.failed"}])

    def test_rejects_error_event(self):
        with self.assertRaisesRegex(ValueError, "error"):
            self.parse([completed(), {"type": "error", "message": "authentication failed"}])

    def test_rejects_truncated_turn(self):
        with self.assertRaisesRegex(ValueError, "unfinished"):
            self.parse([completed(), {"type": "turn.started"}])

    def test_rejects_missing_usage(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            self.parse([{"type": "thread.started"}])

    def test_rejects_invalid_counters(self):
        for event in [completed(10, 20), completed(-1, 0), completed(True, 0), completed(10, 0, 1.5)]:
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.parse([event])

    def test_rejects_unknown_cache_usage(self):
        event = completed()
        del event["usage"]["cached_input_tokens"]
        with self.assertRaises(ValueError):
            self.parse([event])


if __name__ == "__main__":
    unittest.main()
