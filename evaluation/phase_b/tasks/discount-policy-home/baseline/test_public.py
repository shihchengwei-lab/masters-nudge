import unittest
from decimal import Decimal

from checkout import checkout_total


class CheckoutTests(unittest.TestCase):
    def test_student_rate_is_fifteen_percent(self):
        self.assertEqual(Decimal("85.00"), checkout_total(100, True))

    def test_non_student_is_unchanged(self):
        self.assertEqual(Decimal("100.00"), checkout_total(100, False))


if __name__ == "__main__":
    unittest.main()
