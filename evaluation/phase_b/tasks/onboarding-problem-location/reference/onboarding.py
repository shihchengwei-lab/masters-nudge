import unicodedata


def normalize_phone(value):
    normalized = unicodedata.normalize("NFKC", value)
    compact = normalized.replace("-", "").replace(" ", "")
    if len(compact) != 10 or not compact.isascii() or not compact.isdigit():
        raise ValueError("phone must contain ten digits")
    return compact
