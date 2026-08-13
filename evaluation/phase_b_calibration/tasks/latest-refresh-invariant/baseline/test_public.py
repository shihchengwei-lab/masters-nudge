import unittest

from refresh_controller import RefreshController


class RefreshTests(unittest.TestCase):
    def test_sequential_refreshes_render_in_order(self):
        rendered = []
        controller = RefreshController(rendered.append)
        controller.refresh(lambda: "old").join()
        controller.refresh(lambda: "new").join()
        self.assertEqual(["old", "new"], rendered)


if __name__ == "__main__":
    unittest.main()
