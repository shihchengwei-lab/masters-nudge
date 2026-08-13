import unittest

from search_controller import SearchController


class SearchTests(unittest.TestCase):
    def test_sequential_queries_render_latest_result_last(self):
        rendered = []
        controller = SearchController(lambda query, result: rendered.append((query, result)))
        controller.submit("A", lambda query: query.lower()).join()
        controller.submit("B", lambda query: query.lower()).join()
        self.assertEqual(("B", "b"), rendered[-1])


if __name__ == "__main__":
    unittest.main()
