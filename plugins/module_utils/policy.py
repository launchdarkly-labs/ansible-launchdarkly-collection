def policy_argument_spec():
    return dict(
        type="list",
        elements="dict",
        aliases=["statement", "statements", "policies"],
        required_one_of=[["resources", "not_resources"], ["actions", "not_actions"]],
        mutually_exclusive=[["resources", "not_resources"], ["actions", "not_actions"]],
        options=dict(
            resources=dict(type="list", elements="str"),
            not_resources=dict(type="list", elements="str"),
            actions=dict(type="list", elements="str"),
            not_actions=dict(type="list", elements="str"),
            effect=dict(type="str", choices=["allow", "deny"]),
        ),
    )
