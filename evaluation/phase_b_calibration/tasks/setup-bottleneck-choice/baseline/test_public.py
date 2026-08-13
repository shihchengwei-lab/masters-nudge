import unittest

from reminders import schedule_setup_followup
from workspace_setup import normalize_workspace_name


class SetupTests(unittest.TestCase):
    def test_existing_slug_is_unchanged(self):
        self.assertEqual("north-star", normalize_workspace_name("north-star"))

    def test_followup_candidate(self):
        self.assertEqual(
            {"user_id": "u-1", "after_days": 2},
            schedule_setup_followup("u-1"),
        )


if __name__ == "__main__":
    unittest.main()
