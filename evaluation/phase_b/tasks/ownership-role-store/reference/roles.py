VALID_ROLES = {"viewer", "editor", "admin"}

_canonical_roles = {}
gateway_roles = _canonical_roles
billing_roles = _canonical_roles


def reset_state():
    _canonical_roles.clear()


def _validate(role):
    if role not in VALID_ROLES:
        raise ValueError(f"invalid role: {role}")


def _set_role(org_id, user_id, role):
    _validate(role)
    _canonical_roles[(org_id, user_id)] = role


def set_gateway_role(org_id, user_id, role):
    _set_role(org_id, user_id, role)


def set_billing_role(org_id, user_id, role):
    _set_role(org_id, user_id, role)


def get_gateway_role(org_id, user_id):
    return _canonical_roles.get((org_id, user_id))


def get_billing_role(org_id, user_id):
    return _canonical_roles.get((org_id, user_id))


def reconcile_roles():
    return None
