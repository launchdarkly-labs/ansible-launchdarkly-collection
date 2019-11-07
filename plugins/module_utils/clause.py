def clause_argument_spec():
    return dict(
        type="list",
        elements="dict",
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
            negate=dict(type="bool", default=False),
        ),
    )
