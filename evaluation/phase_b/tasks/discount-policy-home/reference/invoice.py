from decimal import Decimal, ROUND_HALF_UP

from discount_policy import student_discount


def invoice_total(subtotal, student_status):
    value = Decimal(str(subtotal)) * (
        Decimal("1") - student_discount(student_status == "student")
    )
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
