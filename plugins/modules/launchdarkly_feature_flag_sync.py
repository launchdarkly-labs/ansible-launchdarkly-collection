#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "0.1.0",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r'''
---
module: launchdarkly_feature_flag_sync
short_description: Sync LaunchDarkly Feature Flags across Environments
description:
     - Sync LaunchDarkly Feature Flags across Environments
version_added: "0.1.0"
options:
    api_key:
        description:
            - LaunchDarkly API Key. May be set as LAUNCHDARKLY_ACCESS_TOKEN environment variable.
        type: str
        required: yes
    project_key:
        description:
            - Project key will group flags together
        default: 'default'
    flag_key:
        description:
            - A unique key that will be used to reference the user segment in this environment.
    environment_key:
        description:
            - A unique key that will be used to determine source environment.
        required: yes
        type: str
    environment_targets:
        description:
            - A list of environments that flag settings will be copied to.
        required: yes
        type: list
    included_actions:
        description:
            - Manage a list of included actions for copying. If not specified all actions are included.
        required: no
        type: list
        choices: ['updateOn', 'updatePrerequisites', 'updateTargets', 'updateRules', 'updateFallthrough', 'updateOffVariation']
    excluded_actions:
        description:
            - Manage a list of excluded actions for copying.
        required: no
        type: list
        choices: ['updateOn', 'updatePrerequisites', 'updateTargets', 'updateRules', 'updateFallthrough', 'updateOffVariation']
'''

EXAMPLES = r'''
# Create a new LaunchDarkly Environment
- launchdarkly_feature_flag_sync:
    environment_key: test-environment-1
    environment_targets:
        - dev
        - staging
        - production
    name: "Test Segment"
    includedActions:
      - updateOn
      - updateRules
'''

RETURN = r'''
'''

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

# from ansible_collections.launchdarkly.collection.plugins.module_utils.base import (
#     configure_instance
# )
from base import configure_instance


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
    for idx, env in enumerate(module.params["environment_targets"]):
        print(env)
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
                feature_flag_copy_body,
            )
        except ApiException as e:
            if e.status == 404:
                err = "user segment key not found"
            else:
                err = json.loads(str(e.body))
            module.exit_json(msg=err)

    module.exit_json(changed=True, msg="feature flags synced")


if __name__ == "__main__":
    main()
