from discount_policy import PARTNER_RATE


def total(amount, *, partner=False):
    rate = PARTNER_RATE if partner else 0.0
    return round(amount * (1 - rate), 2)
