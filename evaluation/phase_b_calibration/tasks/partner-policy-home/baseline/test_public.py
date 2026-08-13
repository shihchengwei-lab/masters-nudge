import unittest

import checkout


class CheckoutTests(unittest.TestCase):
    def test_partner_checkout_uses_new_rate(self):
        self.assertEqual(85.0, checkout.total(100, partner=True))

    def test_regular_checkout_is_unchanged(self):
        self.assertEqual(100.0, checkout.total(100, partner=False))


if __name__ == "__main__":
    unittest.main()
