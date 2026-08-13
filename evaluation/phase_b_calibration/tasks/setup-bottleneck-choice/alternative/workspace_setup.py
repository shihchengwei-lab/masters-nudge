import re


def normalize_workspace_name(value):
    if not isinstance(value, str):
        raise ValueError("workspace name must be text")
    slug = re.sub(r"\s+", "-", value.strip().casefold())
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug or ""):
        raise ValueError("workspace name must become an ASCII slug")
    return slug
