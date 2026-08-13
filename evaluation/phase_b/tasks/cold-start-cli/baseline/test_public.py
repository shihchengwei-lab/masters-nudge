import contextlib
import io
import time
import unittest

import report_cli


class WarmBenchmarkTests(unittest.TestCase):
    def test_repeated_version_calls_are_fast_and_stable(self):
        started = time.perf_counter()
        outputs = []
        for _ in range(20):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                self.assertEqual(0, report_cli.main(["--version"]))
            outputs.append(stream.getvalue())
        elapsed = time.perf_counter() - started
        self.assertLess(elapsed, 0.05)
        self.assertEqual({"report-cli 1.0\n"}, set(outputs))


if __name__ == "__main__":
    unittest.main()
