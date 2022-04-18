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
module: launchdarkly_feature_flag_info
short_description: Return a list of feature flags
description:
     - Return a list of LaunchDarkly feature flags
version_added: "0.2.8"
options:
    project_key:
        description:
            - The project key
        default: 'default'
        required: yes
    key:
        description:
            - The feature flag key
        required: yes
        type: str
    env:
        description:
            - The environment key. Used to filter for a specific environment.
        required: no
        type: str
    tag:
        description:
            - Filter for a specific tag.
        required: no
        type: str
    archived:
        description:
            - Whether to include archived flags.
        required: no
        type: bool
    summary:
        description:
            - Whether to include or exclude a flag's list of prerequisites, targets, and rules in the response. Set to C(false) to include these fields for each flag returned.
        required: no
        type: bool

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Get list of flags filtered to production environment
- launchdarkly_feature_flag_info:
    api_key: api-12345
    project_key: dano-test-project
    env: production
"""

RETURN = r"""
type:
    description: Type of return value
    type: string
    returned: always
results:
    description: List of feature flags.
    returned: always
"""

import inspect
import traceback
import time

LD_IMP_ERR = None
try:
    import launchdarkly_api

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
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(
                required=True,
                type="str",
                no_log=True,
                fallback=(env_fallback, ["LAUNCHDARKLY_ACCESS_TOKEN"]),
            ),
            env=dict(type="str"),
            project_key=dict(type="str", required=True),
            key=dict(type="str"),
            summary=dict(type="bool"),
            archived=dict(type="bool"),
            tag=dict(type="str"),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    # Set up API
    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.FeatureFlagsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    try:
        feature_flags = fetch_flags(module.params, api_instance)
    except launchdarkly_api.rest.ApiException as e:
        fail_exit(module, e)

    if feature_flags.get("items"):
        flags = feature_flags["items"]
    else:
        flags = feature_flags
    module.exit_json(changed=True, feature_flags=flags)


def fetch_flags(params, api_instance):
    try:
        if params.get("key"):
            if params.get("env"):
                response = api_instance.get_feature_flag(
                    params["project_key"],
                    params["key"],
                    env=params["env"],
                )
            else:
                response = api_instance.get_feature_flag(
                    params["project_key"], params["key"]
                )

        else:
            keys = ["project_key", "env", "summary", "archived", "tag"]
            filtered_keys = dict(
                (k, params[k]) for k in keys if k in params and params[k] is not None
            )
            response = api_instance.get_feature_flags(**filtered_keys)

        return response.to_dict()
    except launchdarkly_api.rest.ApiException as e:
        if e.status == 404:
            return None
        else:
            raise


if __name__ == "__main__":
    main()
