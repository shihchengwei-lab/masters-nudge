"""Optional follow-up helpers for workspace setup."""


def pending_messages():
    return []


def schedule_setup_followup(user_id, after_days=2):
    return {"user_id": user_id, "after_days": after_days}
