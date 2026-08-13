VALID_ROLES = {"viewer", "editor", "admin"}

gateway_roles = {}
billing_roles = {}


def reset_state():
    gateway_roles.clear()
    billing_roles.clear()


def _validate(role):
    if role not in VALID_ROLES:
        raise ValueError(f"invalid role: {role}")


def set_gateway_role(org_id, user_id, role):
    _validate(role)
    gateway_roles[(org_id, user_id)] = role


def set_billing_role(org_id, user_id, role):
    _validate(role)
    billing_roles[(org_id, user_id)] = role


def get_gateway_role(org_id, user_id):
    return gateway_roles.get((org_id, user_id))


def get_billing_role(org_id, user_id):
    return billing_roles.get((org_id, user_id))


def reconcile_roles():
    billing_roles.update(gateway_roles)
