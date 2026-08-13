def normalize_workspace_name(value):
    if not isinstance(value, str):
        raise ValueError("workspace name must be text")
    slug = "-".join(value.strip().lower().split())
    if not slug or not slug.isascii():
        raise ValueError("workspace name must become an ASCII slug")
    if any(not (char.islower() or char.isdigit() or char == "-") for char in slug):
        raise ValueError("workspace name must become an ASCII slug")
    return slug
