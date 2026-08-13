def total(amount, *, partner=False):
    rate = 0.15 if partner else 0.0
    return round(amount * (1 - rate), 2)
