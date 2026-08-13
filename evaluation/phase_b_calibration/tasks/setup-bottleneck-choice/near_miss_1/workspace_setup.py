def normalize_workspace_name(value):
    normalized = value.strip().lower()
    if not normalized or not normalized.isascii():
        raise ValueError("workspace name must be ASCII")
    return normalized
