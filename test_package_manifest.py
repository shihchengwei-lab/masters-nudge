import importlib.util
import unittest
from pathlib import Path

from masters_nudge.plugin_inventory import (
    INVENTORY_FILE,
    PACKAGE_MANIFEST,
    package_files,
    runtime_files,
)


ROOT = Path(__file__).resolve().parent


def _load_build_plugin():
    path = ROOT / "tools" / "build_plugin.py"
    spec = importlib.util.spec_from_file_location("build_plugin_for_manifest_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PackageManifestTests(unittest.TestCase):
    def test_manifest_entries_are_unique_and_well_formed(self):
        paths = [entry.path for entry in PACKAGE_MANIFEST]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual({"generated", "static"}, {entry.source for entry in PACKAGE_MANIFEST})
        self.assertTrue(all(Path(path).as_posix() == path for path in paths))

    def test_manifest_covers_every_generated_directory_file(self):
        declared = {entry.path for entry in PACKAGE_MANIFEST}
        discovered = {
            path.relative_to(ROOT).as_posix()
            for directory in ("masters_nudge", "personas")
            for path in (ROOT / directory).rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        }
        self.assertEqual(set(), discovered - declared)

    def test_build_and_runtime_inventories_derive_from_manifest(self):
        build_plugin = _load_build_plugin()
        expected = {Path(path) for path in package_files()}
        expected.add(Path(INVENTORY_FILE))
        self.assertEqual(expected, build_plugin.expected_plugin_files())

        packaged_runtime = set(build_plugin._inventory_payload()["runtime_files"])
        self.assertEqual(set(runtime_files(installed=True)), packaged_runtime)

    def test_optional_ui_is_packaged_but_not_core_runtime(self):
        packaged = set(package_files())
        source_runtime = set(runtime_files(installed=False))
        installed_runtime = set(runtime_files(installed=True))

        self.assertIn("buddy_window.py", packaged)
        self.assertIn("spritesheet.webp", packaged)
        self.assertNotIn("buddy_window.py", source_runtime)
        self.assertNotIn("spritesheet.webp", installed_runtime)
        self.assertIn("masters_nudge/claude_adapter.py", source_runtime)
        self.assertIn("hooks/hooks.json", installed_runtime)


if __name__ == "__main__":
    unittest.main()
