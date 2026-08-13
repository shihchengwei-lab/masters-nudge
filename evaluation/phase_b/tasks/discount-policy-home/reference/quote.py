from decimal import Decimal, ROUND_HALF_UP

from discount_policy import student_discount


def quote_total(subtotal, tags):
    value = Decimal(str(subtotal)) * (
        Decimal("1") - student_discount("student" in tags)
    )
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
