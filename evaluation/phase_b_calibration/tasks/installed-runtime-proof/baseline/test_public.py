import tempfile
import unittest
from pathlib import Path

import installer


class InstallerTests(unittest.TestCase):
    def test_install_returns_copied_script(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "qa package"
            installed = Path(installer.install(target))
            self.assertTrue(installed.is_file())
            self.assertEqual(target.resolve(), installed.parent.resolve())


if __name__ == "__main__":
    unittest.main()
