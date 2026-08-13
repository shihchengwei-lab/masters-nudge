import discount_policy


def total(amount, *, partner=False):
    rate = discount_policy.PARTNER_RATE if partner else 0.0
    return round(amount * (1 - rate), 2)
