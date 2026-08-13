import unittest

import roles


class RoleTests(unittest.TestCase):
    def setUp(self):
        roles.reset_state()

    def test_gateway_write_is_visible_to_both_readers(self):
        roles.set_gateway_role("acme", "u1", "editor")
        self.assertEqual("editor", roles.get_gateway_role("acme", "u1"))
        self.assertEqual("editor", roles.get_billing_role("acme", "u1"))

    def test_invalid_gateway_write_is_rejected(self):
        with self.assertRaises(ValueError):
            roles.set_gateway_role("acme", "u1", "owner")
        self.assertIsNone(roles.get_gateway_role("acme", "u1"))
        self.assertIsNone(roles.get_billing_role("acme", "u1"))


if __name__ == "__main__":
    unittest.main()
