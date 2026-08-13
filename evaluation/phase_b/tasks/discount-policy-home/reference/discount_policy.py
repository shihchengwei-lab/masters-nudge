from decimal import Decimal


STUDENT_DISCOUNT = Decimal("0.15")


def student_discount(eligible):
    return STUDENT_DISCOUNT if eligible else Decimal("0")
