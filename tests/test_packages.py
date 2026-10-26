import tempfile
import unittest
from pathlib import Path

from scripts.check import local_path, read_skill


class PackageTests(unittest.TestCase):
    def test_rejects_traversal_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "package"
            root.mkdir()
            outside = Path(directory) / "outside"
            outside.mkdir()
            (root / "escape").symlink_to(outside, target_is_directory=True)
            for value in ["../outside", "./../outside", "./escape", str(outside)]:
                with self.subTest(value=value), self.assertRaises(ValueError):
                    local_path(root, value)

    def test_resolves_paths_from_package_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skills").mkdir()
            self.assertEqual(local_path(root, "./skills/"), root / "skills")

    def test_rejects_ambiguous_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "example"
            folder.mkdir()
            path = folder / "SKILL.md"
            for header in ['name: example\nname: other\ndescription: "Task"',
                           'name: example\ndescription: Task',
                           'name: wrong\ndescription: "Task"']:
                path.write_text(f"---\n{header}\n---\nInstructions\n", encoding="utf-8")
                with self.subTest(header=header), self.assertRaises(ValueError):
                    read_skill(path)


if __name__ == "__main__":
    unittest.main()
