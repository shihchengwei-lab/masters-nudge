from decimal import Decimal, ROUND_HALF_UP


def quote_total(subtotal, tags):
    percentage = Decimal("0.10") if "student" in tags else Decimal("0")
    value = Decimal(str(subtotal)) * (Decimal("1") - percentage)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
