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
module: launchdarkly_feature_flag
short_description: Manage feature flags
description:
     - Manage LaunchDarkly feature flags
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the Ansible resource
        choices: [ absent, enabled, disabled, deleted, present ]
        default: present
    name:
        description:
            - The name of the flag. If you do not provide one and the underlying API calls require it, this module uses the flag's key.
    kind:
        description:
            - The type of flag. Boolean flags have two variations: C(true) or C(false). Multivariate flags can have more than two variations. The allowed variations depend on the type of flag (string, number, JSON).
        choices: [ bool, str, number, json ]
        default: bool
    temporary:
        description:
            - Toggle if flag is temporary or permanent
        type: bool
        default: 'yes'
    project_key:
        description:
            - The project key
        default: 'default'
        required: yes
    key:
        description:
            - The unique key for this flag. Use this to reference the flag in your code.
        required: yes
        type: str
    variations:
        description:
            - An array of dictionaries containing possible variations for the flag
        type: list
    tags:
        description:
            - An array of tags for this feature flag
        required: no
        type: str
    include_in_snippet:
        description:
            - Whether or not this flag should be made available to the client-side JavaScript SDK
        required: no
        type: bool
    conftest:
        description:
            - Compare input against a Rego policy
        required: no
        suboptions:
            dir:
                description:
                    - Directory to load the Rego policy from
            enabled:
                description:
                    - Whether to run the Conftest policy checks
            namespace:
                description:
                    - Rego namespace to run the tests against

extends_documentation_fragment:
    - launchdarkly_labs.collection.launchdarkly
    - launchdarkly_labs.collection.launchdarkly_conftest
"""

EXAMPLES = r"""
# Create a new flag
- launchdarkly_feature_flag:
    name: example
    kind: bool
    state: present
    temporary: false
    key: example_flag_creation

- launchdarkly_feature_flag:
    name: example
    kind: bool
    key: example_flag_creation1
    state: present
    tags:
     - tag1
     - tag2
    include_in_snippet: true
"""

RETURN = r"""
feature_flag:
    description: Dictionary containing a L(feature flag, https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/FeatureFlag.md)
    type: dict
    returned: on success
"""

import inspect
import traceback
import os
import sys

LD_IMP_ERR = None
try:
    import launchdarkly_api
    from launchdarkly_api.rest import ApiException
    from dictdiffer import diff
    from dictdiffer.utils import PathLimit

    HAS_LD = True
except ImportError:
    LD_IMP_ERR = traceback.format_exc()
    HAS_LD = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback
from ansible.module_utils._text import to_native
from ansible.module_utils.common._json_compat import json
from ansible.module_utils.six import PY2, iteritems, string_types

from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    fail_exit,
    ld_common_argument_spec,
    validate_params,
)


def main():
    required_if = [
        ["kind", "str", ["variations"]],
        ["kind", "json", ["variations"]],
        ["kind", "number", ["variations"]],
    ]

    argument_spec = ld_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(type="str", default="present", choices=["absent", "present"]),
            name=dict(type="str", required_if=["state", "present"]),
            kind=dict(
                choices=["str", "bool", "json", "number"],
                required_if=["state", "present"],
            ),
            project_key=dict(default="default", type="str"),
            key=dict(required=True, type="str"),
            temporary=dict(type="bool", default=True),
            tags=dict(type="list"),
            description=dict(type="str"),
            variations=dict(
                type="list",
                elements="dict",
                options=dict(
                    name=dict(type="str"),
                    value=dict(type="raw"),
                    description=dict(type="str"),
                ),
            ),
            include_in_snippet=dict(type="bool", default=False),
            comment=dict(type="str"),
            maintainer_id=dict(type="str"),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec, required_if=required_if)

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    # Set up API
    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.FeatureFlagsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    if module.params["state"] == "present":
        feature_flag = _fetch_flag(module, api_instance)
        if feature_flag:
            _configure_flag(module, api_instance, feature_flag)
        else:
            _create_flag(module, api_instance)
    elif module.params["state"] == "absent":
        _delete_flag(module, api_instance)


def configure_flag(params, feature_flag):
    patches = []
    if feature_flag:
        if feature_flag.name == params["name"]:
            del params["name"]
        if feature_flag.description == params["description"]:
            del params["description"]
        if feature_flag.include_in_snippet == params["include_in_snippet"]:
            del params["include_in_snippet"]
        if feature_flag.temporary == params["temporary"]:
            del params["temporary"]
        if params["tags"] is not None and set(feature_flag.tags) == set(params["tags"]):
            del params["tags"]
        result = diff(
            feature_flag.to_dict(),
            params,
            ignore=set(
                [
                    "kind",
                    "maintainer_id",
                    "tags",
                    "api_key",
                    "creation_date",
                    "state",
                    "goal_ids",
                    "links",
                    "maintainer",
                    "id",
                    "project_key",
                    "comment",
                    "key",
                    "version",
                    "custom_properties",
                    "salt",
                    "environments",
                ]
            ),
        )
        out_vars = list(result)
        if out_vars:
            changed = [
                variation
                for effects in out_vars
                for variation in effects
                if variation in ["variations"]
            ]
        # TODO fix logic to pass in name and description for bool
        if len(changed) > 0 and params["variations"]:
            _patch_variations(params["variations"], feature_flag.variations, patches)
            del params["variations"]
        else:
            del params["variations"]
        if (
            feature_flag.maintainer_id == params["maintainer_id"]
            or params["maintainer_id"] is None
        ):
            del params["maintainer_id"]
        for key in params:
            if (
                key
                not in [
                    "state",
                    "api_key",
                    "key",
                    "environment_key",
                    "project_key",
                    "kind",
                    "comment",
                    "clone",
                    "variations",
                    "conftest",
                ]
                and params[key] is not None
            ):
                patches.append(_parse_flag_param(params, key, key))
        return patches


def _configure_flag(module, api_instance, feature_flag=None):
    patches = configure_flag(module.params, feature_flag)

    if len(patches) == 0:
        module.exit_json(changed=False, msg="feature flag unchanged")

    if module.params["comment"]:
        comment = module.params["comment"]
    else:
        comment = "Ansible generated operation."
    comments = dict(comment=comment, patch=patches)

    try:
        response, status, headers = api_instance.patch_feature_flag_with_http_info(
            module.params["project_key"], module.params["key"], comments
        )
        module.exit_json(
            changed=True, msg="feature flag updated", content=response.to_dict()
        )
    except ApiException as e:
        fail_exit(module, e)


def _parse_flag_param(params, param_name, key, op="replace"):
    path = "/" + launchdarkly_api.FeatureFlagBody.attribute_map[key]
    return launchdarkly_api.PatchOperation(path=path, op=op, value=params[param_name])


def _create_flag(module, api_instance):
    # Variations can only be set at time of flag creation.
    if module.params["conftest"]["enabled"]:
        validate_params(module)

    if module.params["kind"] == "bool":
        variations = [
            launchdarkly_api.Variation(value=True),
            launchdarkly_api.Variation(value=False),
        ]
    elif module.params["kind"] == "json":
        # No easy way to check isinstance json
        variations = _build_variations(module)
    elif module.params["kind"] == "str":
        if not all(
            isinstance(item, string_types) for item in module.params["variations"]
        ):
            module.exit_json(msg="Variations need to all be strings")
        variations = _build_variations(module)
    elif module.params["kind"] == "number":
        if not all(isinstance(item, int) for item in module.params["variations"]):
            module.exit_json(msg="Variations need to all be integers")
        variations = _build_variations(module)

    feature_flag_config = {
        "key": module.params["key"],
        "variations": variations,
        "temporary": module.params["temporary"],
        "name": module.params["name"],
    }

    try:
        response, status, headers = api_instance.post_feature_flag_with_http_info(
            module.params["project_key"], feature_flag_config
        )

    except ApiException as e:
        err = json.loads(str(e.body))
        if err["code"] == "key_exists":
            module.exit_json(msg="error: Key already exists")
        else:
            fail_exit(module, e)

    _configure_flag(module, api_instance, response)
    module.exit_json(msg="flag successfully created", content=api_response.to_dict())


def _fetch_flag(module, api_instance):
    try:
        response = api_instance.get_feature_flag(
            module.params["project_key"], module.params["key"]
        )
        return response
    except ApiException as e:
        if e.status == 404:
            return None
        else:
            fail_exit(module, e)
    return None


def _delete_flag(module, api_instance):
    feature_flag_config = {
        "project_key": module.params["project_key"],
        "feature_flag_key": module.params["key"],
    }
    try:
        api_response = api_instance.delete_feature_flag(**feature_flag_config)
        module.exit_json(changed=True, msg="feature flag deleted")
    except ApiException as e:
        fail_exit(module, e)


def _build_variations(module):
    variation_list = []
    for item in module.params["variations"]:
        variation_list.append(
            launchdarkly_api.Variation(
                name=item["name"], description=item["description"], value=item["value"]
            )
        )
    return variation_list


def _patch_variations(new_variations, variations, patches):
    # subtract 1 for zero indexing
    oldVariations = len(variations) - 1
    new_variations_len = len(new_variations)
    newIndex = new_variations_len - 1
    i = 0
    if newIndex < oldVariations:
        # iterating over variations for range to be inclusive
        for i in range(new_variations_len, len(variations)):
            patches.append(
                launchdarkly_api.PatchOperation(
                    op="remove", path="/variations/%d" % i, value="needed_for_call"
                )
            )
    else:
        for i in range(new_variations_len):
            if i <= oldVariations:
                patches.append(
                    launchdarkly_api.PatchOperation(
                        op="replace",
                        path="/variations/%d/name" % i,
                        value=new_variations[i]["name"],
                    )
                )
                patches.append(
                    launchdarkly_api.PatchOperation(
                        op="replace",
                        path="/variations/%d/description" % i,
                        value=new_variations[i]["description"],
                    )
                )
                patches.append(
                    launchdarkly_api.PatchOperation(
                        op="replace",
                        path="/variations/%d/value" % i,
                        value=new_variations[i]["value"],
                    )
                )
            else:
                variation = launchdarkly_api.Variation(
                    name=new_variations[i]["name"],
                    description=new_variations[i]["description"],
                    value=new_variations[i]["value"],
                )
                patches.append(
                    launchdarkly_api.PatchOperation(
                        op="add", path="/variations/%d" % i, value=variation
                    )
                )
                return patches
    return patches


if __name__ == "__main__":
    main()
