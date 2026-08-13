import unittest

from exports import export_csv


class CsvTests(unittest.TestCase):
    def test_custom_delimiter(self):
        rows = [{"name": "Ada", "score": 9}]
        self.assertEqual("name;score\nAda;9\n", export_csv(rows, delimiter=";"))

    def test_default_delimiter(self):
        rows = [{"name": "Ada", "score": 9}]
        self.assertEqual("name,score\nAda,9\n", export_csv(rows))


if __name__ == "__main__":
    unittest.main()
