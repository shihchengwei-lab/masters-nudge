def normalize_workspace_name(value):
    if not value or not value.isascii():
        raise ValueError("workspace name must be an ASCII slug")
    if any(not (char.islower() or char.isdigit() or char == "-") for char in value):
        raise ValueError("workspace name must be an ASCII slug")
    return value
