def normalize_phone(value):
    if len(value) != 10 or not value.isascii() or not value.isdigit():
        raise ValueError("phone must contain ten ASCII digits")
    return value
