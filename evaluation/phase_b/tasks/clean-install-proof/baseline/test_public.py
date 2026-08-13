import tempfile
import unittest
from pathlib import Path

import installer
import mn_cli


class InstallTests(unittest.TestCase):
    def test_source_greeting(self):
        self.assertEqual("Hello, Ada!", mn_cli.greeting_for("Ada"))

    def test_installer_returns_copied_script(self):
        with tempfile.TemporaryDirectory() as raw:
            installed = installer.install(Path(raw))
            self.assertTrue(Path(installed).is_file())


if __name__ == "__main__":
    unittest.main()
