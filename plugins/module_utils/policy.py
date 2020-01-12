from __future__ import absolute_import, division, print_function

__metaclass__ = type

def policy_argument_spec():
    return dict(
        type="list",
        elements="dict",
        aliases=["statement", "statements", "policies"],
        options=dict(
            resources=dict(type="list", elements="str"),
            actions=dict(type="list", elements="str", default="*"),
            effect=dict(type="str", choices=["allow", "deny"]),
        ),
    )
