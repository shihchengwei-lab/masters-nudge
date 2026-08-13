import unittest

from onboarding import normalize_phone


class PhoneTests(unittest.TestCase):
    def test_plain_digits_remain_unchanged(self):
        self.assertEqual("0912345678", normalize_phone("0912345678"))

    def test_letters_are_rejected(self):
        with self.assertRaises(ValueError):
            normalize_phone("0912ABC678")


if __name__ == "__main__":
    unittest.main()
