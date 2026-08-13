from decimal import Decimal, ROUND_HALF_UP


def invoice_total(subtotal, student_status):
    discount = Decimal("0.10") if student_status == "student" else Decimal("0")
    value = Decimal(str(subtotal)) * (Decimal("1") - discount)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
