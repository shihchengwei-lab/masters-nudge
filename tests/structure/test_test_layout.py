from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_ROOT = REPO_ROOT / "tests"
TEST_CATEGORIES = {
    "contracts",
    "core",
    "hosts",
    "packaging",
    "providers",
    "structure",
}


class TestTestLayout(unittest.TestCase):
    def test_repository_root_has_no_test_modules(self):
        root_tests = sorted(path.name for path in REPO_ROOT.glob("test_*.py"))
        self.assertEqual(root_tests, [])

    def test_every_test_module_belongs_to_a_named_category(self):
        uncategorized = sorted(
            path.relative_to(TEST_ROOT).as_posix()
            for path in TEST_ROOT.rglob("test_*.py")
            if path.parent.name not in TEST_CATEGORIES
        )
        self.assertEqual(uncategorized, [])

    def test_categories_are_importable_for_unittest_discovery(self):
        missing = sorted(
            category
            for category in TEST_CATEGORIES
            if not (TEST_ROOT / category / "__init__.py").is_file()
        )
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
