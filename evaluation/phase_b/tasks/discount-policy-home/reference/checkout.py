from decimal import Decimal, ROUND_HALF_UP

from discount_policy import student_discount


def checkout_total(subtotal, is_student):
    value = Decimal(str(subtotal)) * (Decimal("1") - student_discount(is_student))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
