def clause_argument_spec():
    return dict(
        type="list",
        elements="dict",
        apply_defaults=True,
        options=dict(
            attribute=dict(type="str"),
            op=dict(
                type="str",
                choices=[
                    "in",
                    "endsWith",
                    "startsWith",
                    "matches",
                    "contains",
                    "lessThan",
                    "lessThanOrEqual",
                    "greaterThanOrEqual",
                    "before",
                    "after",
                    "segmentMatch",
                    "semVerEqual",
                    "semVerLessThan",
                    "semVerGreaterThan",
                ],
            ),
            values=dict(type="list"),
            negate=dict(apply_defaults=True,type="bool", default=True),
        ),
    )
