def normalize_workspace_name(value):
    slug = value.strip().lower().replace(" ", "-")
    if not slug or not slug.isascii():
        raise ValueError("workspace name must be ASCII")
    return slug
