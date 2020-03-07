#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "0.1.0",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: launchdarkly_webhook
short_description: Manage LaunchDarkly Webhooks
description:
     - Manage LaunchDarkly Webhooks
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the resource.
        choices: [ absent, present ]
        default: present
    name:
        description:
            - A human-readable name for your webhook.
        type: str
    webhook_id:
        description:
            - Webhook id. Required when updating resource.
        type: str
    url:
        description:
            - The URL of the remote webhook.
        type: str
    secret:
        description:
            - If sign is true, and the secret attribute is omitted, LaunchDarkly will automatically generate a secret for you.
        type: str
    sign:
        description:
            - If sign is false, the webhook will not include a signature header, and the secret can be omitted.
        type: bool
    enabled:
        description:
            - Whether this webhook is enabled or not.
        type: bool

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Create a new LaunchDarkly Webhook
- launchdarkly_webhook:
    state: present
    project_key: test-project-1
    environment_key: test-environment-1
    user_segment_key: test-key-1
    name: "Test Segment"
    description: "This is a testing segment"
    rules:
        clauses:
          - attribute: testAttribute
            op: contains
            values:
              - 2
              - 3
            negate: true
    tags:
      - blue
      - green
    included:
      - test1
      - test2
    excluded:
      - test3
      - test4
"""

RETURN = r"""
---
webhook:
    description: Dictionary containing a L(Webhook, https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/Webhook.md)
    type: dict
    returned: on success
"""

import inspect
import traceback

LD_IMP_ERR = None
try:
    import launchdarkly_api
    from launchdarkly_api.rest import ApiException
    from dictdiffer import diff

    HAS_LD = True
except ImportError:
    LD_IMP_ERR = traceback.format_exc()
    HAS_LD = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback
from ansible.module_utils._text import to_native
from ansible.module_utils.common._json_compat import json
from ansible.module_utils.six import PY2, iteritems, string_types
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.clause import (
    clause_argument_spec,
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    _patch_path,
    fail_exit,
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.policy import (
    policy_argument_spec,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                type="str",
                default="present",
                choices=["absent", "present", "enabled", "disabled"],
            ),
            api_key=dict(
                required=True,
                type="str",
                no_log=True,
                fallback=(env_fallback, ["LAUNCHDARKLY_ACCESS_TOKEN"]),
            ),
            name=dict(type="str"),
            sign=dict(type="bool", default=False),
            url=dict(type="str"),
            webhook_id=dict(type="str"),
            tags=dict(type="list", elements="str"),
            statements=policy_argument_spec(),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.WebhooksApi(
        launchdarkly_api.ApiClient(configuration)
    )

    if module.params["state"] in ["present", "enabled"]:
        webhook = _fetch_webhook(module, api_instance)
        if webhook:
            _configure_webhook(module, api_instance, webhook)
        else:
            _create_webhook(module, api_instance)
    elif module.params["state"] == "absent":
        _delete_webhook(module, api_instance)


def _parse_webhook_param(module, param_name, key=None):
    if key is None:
        key = launchdarkly_api.Webhook.attribute_map[param_name]
    path = "/" + key
    patch = dict(path=path, op="replace", value=module.params[param_name])
    print(patch)
    return launchdarkly_api.PatchOperation(**patch)


def _delete_webhook(module, api_instance):
    try:
        api_instance.delete_webhook(module.params["webhook_id"])
        module.exit_json(msg="successfully deleted webhook")
    except ApiException as e:
        fail_exit(module, e)


def _create_webhook(module, api_instance):
    if module.params["state"] == "enabled":
        webhook_status = True
    else:
        webhook_status = False

    webhook_config = {
        "url": module.params["url"],
        "sign": module.params["sign"],
        "on": webhook_status,
    }

    if module.params.get("secret"):
        webhook_config["secret"] = module.params["secret"]
    webhook_config["name"] = (
        module.params["name"] if module.params.get("name") else module.params["url"]
    )

    if module.params["tags"]:
        webhook_config["tags"] = module.params["tags"]

    if module.params["statements"]:
        filtered_statements = []
        for statement in module.params["statements"]:
            filtered_statements.append(
                dict(
                    (launchdarkly_api.Statement.attribute_map[k], v)
                    for k, v in statement.items()
                    if v is not None
                )
            )
        webhook_config["statements"] = filtered_statements
    webhook_body = launchdarkly_api.WebhookBody(**webhook_config)

    try:
        api_response = api_instance.post_webhook(webhook_body)
        module.params["webhook_id"] = api_response.id
    except ApiException as e:
        fail_exit(module, e)

    module.exit_json(
        changed=True, msg="webhook created", webhook=api_response.to_dict()
    )


def _configure_webhook(module, api_instance, webhook=None):
    patches = []
    if webhook:
        if webhook.name == module.params["name"] or module.params["name"] is None:
            del module.params["name"]
        if webhook.url == module.params["url"] or module.params["url"] is None:
            del module.params["url"]
        if set(webhook.tags) == set(module.params["tags"]):
            del module.params["tags"]
        # Loop over statements comparing
        if module.params["statements"] is not None:
            if len(module.params["statements"]) < len(webhook.statements):
                oldStatements = len(webhook.statements) - 1
                newStatements = len(module.params["statements"])
                newIndex = newStatements - 1
                i = 0
                if newIndex < oldStatements:
                    # iterating over statements for range to be inclusive
                    for i in range(newStatements, len(webhook.statements)):
                        patches.append(
                            launchdarkly_api.PatchOperation(
                                op="remove",
                                path="/statements/%d" % i,
                                value="needed_for_call",
                            )
                        )
            for idx, statement in enumerate(module.params["statements"]):
                if idx > len(webhook.statements) - 1:
                    tmp_results = ["break"]
                    break
                tmp_results = diff(statement, webhook.statements[idx])
            statement_results = list(tmp_results)
            if len(statement_results) == 0:
                del module.params["statements"]

    for key in module.params:
        if key not in ["state", "api_key", "sign", "webhook_id"]:
            if module.params[key] is not None:
                patches.append(_parse_webhook_param(module, key))

    if len(patches) > 0:
        try:
            api_response = api_instance.patch_webhook(
                module.params["webhook_id"], patch_delta=patches
            )
        except ApiException as e:
            if e.status == 404:
                module.exit_json(failed=True, msg="webhook id not found")
            else:
                fail_exit(module, e)

    module.exit_json(
        msg="webhook successfully configured", webhook=api_response.to_dict()
    )


def _fetch_webhook(module, api_instance):
    if module.params["webhook_id"] is not None:
        try:
            # Get a webhook given an id.
            webhook = api_instance.get_webhook(module.params["webhook_id"])
            return webhook
        except ApiException as e:
            if e.status == 404:
                return False
            else:
                fail_exit(module, e)
    else:
        return False


if __name__ == "__main__":
    main()
