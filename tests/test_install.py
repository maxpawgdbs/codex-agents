import io
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.install import ARCHIVE_URL, IGNORE_END, IGNORE_START, collect_files, install

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def test_installs_capabilities_and_ignores_them_in_existing_project(self):
        files = collect_files(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            subprocess.run(["git", "init", "-q", str(target)], check=True)
            (target / "app.py").write_text("print('project')\n")
            (target / "AGENTS.md").write_text("My project instructions\n")
            (target / ".codex").mkdir()
            (target / ".codex/config.toml").write_text('model = "my-choice"\n')
            (target / ".gitignore").write_bytes(b"node_modules/\r\n")
            self.assertEqual(install(target, files), 9)
            ignored = subprocess.run(["git", "-C", str(target), "check-ignore", *files],
                                     check=True, capture_output=True, text=True)
            self.assertEqual(set(ignored.stdout.splitlines()), set(files))
            self.assertEqual((target / "AGENTS.md").read_text(), "My project instructions\n")
            self.assertEqual((target / ".codex/config.toml").read_text(), 'model = "my-choice"\n')
            self.assertEqual(sorted(path.name for path in target.iterdir()),
                             [".agents", ".codex", ".git", ".gitignore", "AGENTS.md", "app.py"])
            ignore_before = (target / ".gitignore").read_bytes()
            self.assertTrue(ignore_before.startswith(b"node_modules/\r\n"))
            self.assertEqual(install(target, files), 0)
            self.assertEqual((target / ".gitignore").read_bytes(), ignore_before)

    def test_collision_leaves_project_untouched(self):
        files = collect_files(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            collision = target / ".codex/agents/scout.toml"
            collision.parent.mkdir(parents=True)
            collision.write_text("my existing role\n")
            with self.assertRaisesRegex(ValueError, "Existing file differs"):
                install(target, files)
            self.assertEqual(collision.read_text(), "my existing role\n")
            self.assertFalse((target / ".agents").exists())
            self.assertFalse((target / ".gitignore").exists())

    def test_symlink_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            outside = Path(directory) / "outside"
            target.mkdir()
            outside.mkdir()
            (target / ".agents").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                install(target, {".agents/skills/example/SKILL.md": b"instructions"})
            self.assertEqual(list(outside.iterdir()), [])

    def test_malformed_ignore_block_is_rejected_before_copying(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".gitignore").write_text(IGNORE_START + "\n")
            with self.assertRaisesRegex(ValueError, "Malformed"):
                install(target, collect_files(ROOT))
            self.assertFalse((target / ".agents").exists())

    def test_download_selects_capabilities_without_extracting_repository(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            archive.writestr("codex-agents-main/README.md", "Not installed")
            archive.writestr("codex-agents-main/.git/config", "Not installed")
            archive.writestr("codex-agents-main/.agents/skills/example/SKILL.md", "Instructions")
            archive.writestr("codex-agents-main/plugins/session-tools/skills/session-handoff/SKILL.md", "Handoff")
        with patch("scripts.install.urllib.request.urlopen", return_value=io.BytesIO(data.getvalue())) as download:
            files = collect_files()
        self.assertEqual(download.call_args.args[0].full_url, ARCHIVE_URL)
        self.assertEqual(set(files), {".agents/skills/example/SKILL.md", ".agents/skills/session-handoff/SKILL.md"})

    def test_existing_ignore_rules_after_managed_block_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".gitignore").write_text(f"dist/\n{IGNORE_START}\n/old-path\n{IGNORE_END}\n.env\n")
            install(target, collect_files(ROOT))
            updated = (target / ".gitignore").read_text()
            self.assertTrue(updated.startswith("dist/\n"))
            self.assertTrue(updated.endswith(".env\n"))
            self.assertNotIn("/old-path", updated)
            self.assertEqual(updated.count(IGNORE_START), 1)


if __name__ == "__main__":
    unittest.main()
