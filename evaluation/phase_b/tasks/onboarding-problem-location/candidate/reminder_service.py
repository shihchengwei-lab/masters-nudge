from dataclasses import dataclass


@dataclass
class Reminder:
    user_id: str
    phone: str


class ReminderQueue:
    def __init__(self):
        self.pending = []

    def enqueue_incomplete_profile(self, user_id, phone):
        self.pending.append(Reminder(user_id, phone))
