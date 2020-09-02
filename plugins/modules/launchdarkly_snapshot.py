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
module: launchdarkly_snapshot
short_description: Return a snapshot of your Project
description:
     - Return value from Feature Flag Evaluation
version_added: "0.3.5"
options:
    project_key:
        description:
            - Project key will group flags together
        default: 'default'
        required: yes
    env:
        description:
            - Filter for a specific environment.
        required: no
        type: str
    archived:
        description:
            - Include archived flags.
        required: no
        type: bool
    summary:
        description:
            - Flags will not include their list of prerequisites, targets or rules. Set to false to include these fields for each flag returned
        required: no
        type: bool
        default: false

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Get list of flags filtered to production environment.
- launchdarkly_snapshot:
    api_key: api-12345
    project_key: dano-test-project
"""

RETURN = r"""
type:
    description: Type of return value
    type: string
    returned: always
results:
    description: List of Feature Flags.
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

# from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
#     configure_instance,
#     fail_exit,
# )

# from ansible_collections.launchdarkly_labs.collection.plugins.modules.launchdarkly_feature_flag_info import (
#     fetch_flags
# )

from base import (
    configure_instance,
    fail_exit,
)

from launchdarkly_feature_flag_info import fetch_flags


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
            summary=dict(type="bool"),
            archived=dict(type="bool"),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    # Set up API
    configuration = configure_instance(module.params["api_key"])
    api_instance_project = launchdarkly_api.ProjectsApi(
        launchdarkly_api.ApiClient(configuration)
    )
    api_instance_flag = launchdarkly_api.FeatureFlagsApi(
        launchdarkly_api.ApiClient(configuration)
    )
    api_instance_segment = launchdarkly_api.UserSegmentsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    try:
        project = api_instance_project.get_project(module.params["project_key"])
        feature_flags = fetch_flags(module.params, api_instance_flag)
        segments = {}
        for env in project.environments:
            segment = api_instance_segment.get_user_segments(
                module.params["project_key"], env.key
            )
            segments[env.key] = segment.to_dict()["items"]
    except launchdarkly_api.rest.ApiException as e:
        fail_exit(module, e)

    if feature_flags.get("items"):
        flags = feature_flags["items"]
    else:
        flags = feature_flags

    module.exit_json(
        changed=True, project=project.to_dict(), feature_flags=flags, segments=segments
    )


if __name__ == "__main__":
    main()
