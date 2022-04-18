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
module: launchdarkly_user_segment_sync
short_description: Copy a user segment across environments
description:
     - Copy a LaunchDarkly user segment across environments
version_added: "0.1.0"
options:
    project_key:
        description:
            - The project key
        default: 'default'
        type: str
    user_segment_key:
        description:
            - The user segment key for this environment
        type: str
        required: yes
    environment_key:
        description:
            - The environment key for the source environment
        required: yes
        type: str
    environment_targets:
        description:
            - A list of environments the user segment will be copied to
        required: yes
        type: list
    includedActions:
        description:
            - Manage a list of included actions for copying
        required: no
        type: list
        choices: ['updateTargets', 'updateRules']
    excludedActions:
        description:
            - Manage a list of excluded actions for copying
        required: no
        type: list
        choices: [updateTargets', 'updateRules']

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Copy a user segment to multiple environments
- launchdarkly_user_segment_sync:
    environment_key: test-environment-1
    environment_targets:
        - dev
        - staging
        - production
    name: "Test Segment"
    includedActions:
      - updateOn
      - updateRules
"""

RETURN = r"""
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

from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    fail_exit,
    ld_common_argument_spec,
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
            environment_key=dict(type="str", required=True),
            project_key=dict(type="str", required=True),
            user_segment_key=dict(type="str", required=True),
            environment_targets=dict(type="list", required=True),
            included_actions=dict(
                type="list", choices=["updateTargets", "updateRules"]
            ),
            excluded_actions=dict(
                type="list", choices=["updateTargets", "updateRules"]
            ),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.UserSegmentsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    _configure_user_sync(module, api_instance)


def _configure_user_sync(module, api_instance):

    user_segment = api_instance.get_user_segment(
        module.params["project_key"],
        module.params["environment_key"],
        module.params["user_segment_key"],
    )

    new_segment = launchdarkly_api.UserSegmentBody(
        name=user_segment.name,
        key=user_segment.key,
        description=user_segment.description,
        tags=user_segment.tags,
    )

    for idx, env in enumerate(module.params["environment_targets"]):
        patches = []
        try:
            response, status, headers = api_instance.post_user_segment_with_http_info(
                module.params["project_key"], env, new_segment
            )
        except ApiException as e:
            if e.status == 409:
                (
                    response,
                    status,
                    headers,
                ) = api_instance.get_user_segment_with_http_info(
                    module.params["project_key"], env, module.params["user_segment_key"]
                )
                if user_segment.name is not None and user_segment.name != response.name:
                    patches.append(_patch_op("replace", "/name", user_segment.name))
                if (
                    user_segment.description is not None
                    and user_segment.description != response.description
                ):
                    patches.append(
                        _patch_op("replace", "/description", user_segment.description)
                    )
                if user_segment.tags is not None and set(user_segment.tags) != set(
                    response.tags
                ):
                    patches.append(_patch_op("replace", "/tags", user_segment.tags))
            else:
                fail_exit(module, e)

        if (
            module.params["included_actions"] is None
            or (
                "updateTargets" in module.params["included_actions"]
                or "updateTargets" not in module.params["excluded_actions"]
            )
            and (
                set(response.included) != set(user_segment.included)
                or set(response.excluded) != set(user_segment.excluded)
            )
        ):
            patches.append(_patch_op("replace", "/included", user_segment.included))
            patches.append(_patch_op("replace", "/excluded", user_segment.excluded))

        if module.params["included_actions"] is None or (
            "updateRules" in module.params["included_actions"]
            or "updateRules" not in module.params["excluded_actions"]
        ):
            for rule in user_segment.rules:
                patches.append(
                    launchdarkly_api.PatchOperation(
                        op="add", path="/rules", value=user_segment.rules
                    )
                )

        try:
            response, status, headers = api_instance.patch_user_segment_with_http_info(
                module.params["project_key"], env, user_segment.key, patches
            )
        except ApiException as e:
            if e.status == 404:
                module.exit_json(
                    failed=True,
                    msg="user segment key: %s not found"
                    % module.params["user_segment_key"],
                )
            else:
                fail_exit(module, e)

    module.exit_json(
        changed=True, msg="feature flags synced", user_segment=response.to_dict()
    )


if __name__ == "__main__":
    main()
