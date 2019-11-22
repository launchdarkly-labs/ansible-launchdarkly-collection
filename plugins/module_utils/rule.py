# from clause import clause_argument_spec

from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.clause import (
    clause_argument_spec,
)


def rule_argument_spec():
    return dict(
        type="list",
        elements="dict",
        options=dict(
            state=dict(
                type="str", default="present", choices=["absent", "present", "add"]
            ),
            variation=dict(type="int"),
            rollout=dict(
                type="list",
                elements="dict",
                options=dict(variation=dict(type="int"), weight=dict(type="int")),
            ),
            clauses=clause_argument_spec(),
        ),
    )
