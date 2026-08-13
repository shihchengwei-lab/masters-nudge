import unittest

from exports import export_csv


class CsvTests(unittest.TestCase):
    def test_pipe_delimiter(self):
        rows = [{"id": 1, "name": "Ada"}]
        self.assertEqual("id|name\n1|Ada\n", export_csv(rows, delimiter="|"))

    def test_delimiter_must_be_one_character(self):
        with self.assertRaises(ValueError):
            export_csv([{"id": 1}], delimiter="::")


if __name__ == "__main__":
    unittest.main()
