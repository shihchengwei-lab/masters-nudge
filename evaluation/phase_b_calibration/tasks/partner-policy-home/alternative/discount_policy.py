PARTNER_RATE = 0.15


def rate_for(*, partner):
    return PARTNER_RATE if partner else 0.0
