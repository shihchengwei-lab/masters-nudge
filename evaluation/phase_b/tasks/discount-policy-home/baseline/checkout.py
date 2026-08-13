from decimal import Decimal, ROUND_HALF_UP


def checkout_total(subtotal, is_student):
    rate = Decimal("0.10") if is_student else Decimal("0")
    value = Decimal(str(subtotal)) * (Decimal("1") - rate)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
