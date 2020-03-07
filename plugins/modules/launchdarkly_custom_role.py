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
module: launchdarkly_custom_role
short_description: Manage LaunchDarkly Custom Roles
description:
    - Manager LaunchDarkly Custom Roles
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the resource
        choices: [ absent, present ]
        default: present
    key:
        description:
            - Unique key to identify Custom Role
        type: str
        required: yes
    name:
        description:
            - A human-readable name for your webhook
        type: str
        required: no
    description:
        description:
            - Description of the custom role
        type: str
        required: no
    policies:
        description:
            - Policies to attach to the role
        type: dict
        required: yes
        suboptions:
            resources:
                description:
                    - Resource to use in policy
                type: list
                required: no
            not_resources:
                description:
                    - inverse of Resource to use in policy
                type: list
                required: no
            actions:
                description:
                    - Identify actions of policy
                type: str
            not_actions:
                description:
                    - inverse of actions for policy
                type: str
            effect:
                description:
                    - Defines whether the statement allows or denies access to the named resources and actions.
                choices: ["allow", "deny"]
                type: str

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
- launchdarkly_custom_role:
    state: present
    name: "My Custom Role"
    policies:
        resources:
          - "proj/*:env/*:flag/test_flag"
        actions:
          - "*"
        effect: allow
"""

RETURN = r"""
---
custom_role:
    description: Dictionary containing a L(Custom Role, https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/CustomRole.md)
    type: dict
    returned: on success
"""

import inspect
import traceback

LD_IMP_ERR = None
try:
    import launchdarkly_api
    from launchdarkly_api.rest import ApiException

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
            state=dict(type="str", default="present", choices=["absent", "present"]),
            api_key=dict(
                required=True,
                type="str",
                no_log=True,
                fallback=(env_fallback, ["LAUNCHDARKLY_ACCESS_TOKEN"]),
            ),
            key=dict(type="str", required=True, aliases=["custom_role_key"]),
            name=dict(type="str"),
            description=dict(type="str"),
            policy=policy_argument_spec(),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.CustomRolesApi(
        launchdarkly_api.ApiClient(configuration)
    )

    if module.params["state"] == "present":
        if module.params.get("key") and _fetch_custom_role(module, api_instance):
            _configure_custom_role(module, api_instance)
        else:
            _create_custom_role(module, api_instance)
    elif module.params["state"] == "absent":
        _delete_custom_role(module, api_instance)


def _parse_custom_role_param(module, param_name, key=None):
    if key is None:
        key = launchdarkly_api.CustomRole.attribute_map[param_name]
    path = "/" + key
    if param_name == "policy":
        policies = _parse_policies(module.params["policy"])
        patch = dict(path=path, op="replace", value=policies)
    else:
        patch = dict(path=path, op="replace", value=module.params[param_name])

    return launchdarkly_api.PatchOperation(**patch)


def _parse_policies(policies):
    parsed_policies = []
    for policy in policies:
        parsed_policies.append(launchdarkly_api.Policy(**policy))
    return parsed_policies


def _delete_custom_role(module, api_instance):
    try:
        api_instance.delete_custom_role(module.params["key"])
        module.exit_json(msg="successfully deleted custom role")
    except ApiException as e:
        fail_exit(module, e)


def _create_custom_role(module, api_instance):
    name = (
        module.params["name"]
        if module.params["name"] is not None
        else module.params["key"]
    )

    custom_role_config = {"key": module.params["key"], "name": name}

    if module.params["policy"]:
        policies = _parse_policies(module.params["policy"])
        custom_role_config["policy"] = policies

    custom_role_body = launchdarkly_api.CustomRoleBody(**custom_role_config)

    try:
        response, status, headers = api_instance.post_custom_role_with_http_info(
            custom_role_body
        )
    except ApiException as e:
        module.exit_json(msg=to_native(e.reason))

    module.exit_json(
        changed=True,
        msg="custom role created",
        custom_role=to_native(response.to_dict()),
    )


def _configure_custom_role(module, api_instance):
    patches = []
    for key in module.params:
        if key not in ["state", "api_key", "key"] and module.params[key] is not None:
            patches.append(_parse_custom_role_param(module, key))

    if len(patches) > 0:
        try:
            api_response = api_instance.patch_custom_role(
                module.params["key"], patch_delta=patches
            )
        except ApiException as e:
            if e.status == 404:
                module.exit_json(
                    failed=True, msg="custom role: %s not found" % module["key"]
                )
            else:
                fail_exit(module, e)

        module.exit_json(
            changed=True, msg="successfully updated custom role: %s" % api_response.key
        )
    else:
        module.exit_json(changed=False, msg="custom role unchanged")


def _fetch_custom_role(module, api_instance):
    if module.params["key"] is not None:
        try:
            # Get a webhook given an id.
            api_instance.get_custom_role(module.params["key"])
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            else:
                module.exit_json(msg=to_native(e.reason))
    else:
        return False


if __name__ == "__main__":
    main()
