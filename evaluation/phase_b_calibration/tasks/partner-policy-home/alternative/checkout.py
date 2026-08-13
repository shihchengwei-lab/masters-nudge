from discount_policy import rate_for


def total(amount, *, partner=False):
    return round(amount * (1 - rate_for(partner=partner)), 2)
