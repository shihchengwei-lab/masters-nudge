import contextlib
import io
import unittest

import tool


class ToolTests(unittest.TestCase):
    def capture(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            tool.main(args)
        return output.getvalue()

    def test_version_output(self):
        self.assertEqual("tool 1.0\n", self.capture(["--version"]))

    def test_details_output(self):
        self.assertEqual("alpha:5\n", self.capture(["--details", "alpha"]))


if __name__ == "__main__":
    unittest.main()
