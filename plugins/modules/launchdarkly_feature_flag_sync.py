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
module: launchdarkly_feature_flag_sync
short_description: Sync flag settings across environments
description:
     - Sync LaunchDarkly feature flag settings across environments. To learn more, read L(Comparing and copying flag settings between two environments, https://docs.launchdarkly.com/home/code/flag-compare-copy#comparing-and-copying-flag-settings-between-two-environments).
version_added: "0.1.0"
options:
    project_key:
        description:
            - The project key
        default: 'default'
        type: str
    flag_key:
        description:
            - The flag key
        type: str
        required: yes
    environment_key:
        description:
            - The envionment key for the source environment
        required: yes
        type: str
    environment_targets:
        description:
            - A list of environment keys for the destination environments. These are the environments that flag settings will be copied to.
        required: yes
        type: list
    included_actions:
        description:
            - Manage a list of included actions to copy. If you do not specify any, all actions are included.
        required: no
        type: list
        choices: ['updateFallthrough', 'updateOn', 'updateOffVariation', 'updatePrerequisites', 'updateRules', 'updateTargets']
    excluded_actions:
        description:
            - Manage a list of excluded actions for copying.
        required: no
        type: list
        choices: ['updateFallthrough', 'updateOn', 'updateOffVariation', 'updatePrerequisites', 'updateRules', 'updateTargets']

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Sync LaunchDarkly feature flag settings across environments
- launchdarkly_feature_flag_sync:
    environment_key: test-environment-1
    environment_targets:
        - dev
        - staging
        - production
    flag_key: test_flag_1
    project_key: test_project
    included_actions:
      - updateOn
      - updateRules
"""

RETURN = r"""
feature_flag:
    description: Dictionary containing a L(feature flag, https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/FeatureFlag.md)
    type: dict
    returned: on success
"""

import inspect
import traceback
import time

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
    reset_rate,
    fail_exit,
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
            flag_key=dict(type="str", required=True),
            environment_targets=dict(type="list", required=True),
            included_actions=dict(
                type="list",
                choices=[
                    "updateOn",
                    "updatePrerequisites",
                    "updateTargets",
                    "updateRules",
                    "updateFallthrough",
                    "updateOffVariation",
                ],
            ),
            excluded_actions=dict(
                type="list",
                choices=[
                    "updateOn",
                    "updatePrerequisites",
                    "updateTargets",
                    "updateRules",
                    "updateFallthrough",
                    "updateOffVariation",
                ],
            ),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.FeatureFlagsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    _configure_flag_sync(module, api_instance)


def _configure_flag_sync(module, api_instance):
    results = []
    max_targets = len(module.params["environment_targets"]) - 1
    for idx, env in enumerate(module.params["environment_targets"]):
        source = {"key": module.params["environment_key"]}

        target = {"key": env}

        feature_flag_copy_body = {"source": source, "target": target}

        if module.params["included_actions"] is not None:
            feature_flag_copy_body["included_actions"] = module.params[
                "included_actions"
            ]

        if module.params["excluded_actions"] is not None:
            feature_flag_copy_body["excluded_actions"] = module.params[
                "excluded_actions"
            ]

        try:
            response, status, headers = api_instance.copy_feature_flag_with_http_info(
                module.params["project_key"],
                module.params["flag_key"],
                launchdarkly_api.FeatureFlagCopyBody(**feature_flag_copy_body),
            )

            if idx == max_targets:
                # LD Returns a FeatureFlag Object containing all Environments. Only need last one.
                feature_flag = response.to_dict()

        except ApiException as e:
            if e.status == 429:
                time.sleep(reset_rate(e.headers["X-RateLimit-Reset"]))
                api_instance.copy_feature_flag_with_http_info(
                    module.params["project_key"],
                    module.params["flag_key"],
                    launchdarkly_api.FeatureFlagCopyBody(**feature_flag_copy_body),
                )
            else:
                fail_exit(module, e)

    module.exit_json(
        changed=True, msg="feature flags synced", feature_flag=feature_flag
    )


if __name__ == "__main__":
    main()
