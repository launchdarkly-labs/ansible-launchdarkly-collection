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
module: launchdarkly_test_generator
short_description: Create a JSON file for testing
description:
     - Create a JSON file for local testing
version_added: "0.2.0"
options:
    sdk_key:
        description:
            - SDK Key to retrieve flags for an environment.
        default: 'default'
        required: yes
        type: str
    overrides_flag:
        description:
            - override specific keys
        required: no
        type: list
"""

EXAMPLES = r"""
# Create a new LaunchDarkly Project with tags
  - name: Generate Test JSON
    launchdarkly_test_generator:
      sdk_key: sdk-test-123456
      overrides_flag:
        - example_test_flag: True
    register: results
"""

RETURN = r"""
content:
    description: Dictionary containing a JSON object that can be used as a file source.
    type: json
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
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.module_utils.common._json_compat import json
from ansible.module_utils.six import PY2, iteritems, string_types
from ansible.module_utils.urls import *
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.environment import (
    ld_env_arg_spec,
    env_ld_builder,
)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            sdk_key=dict(
                required=True,
                type="str",
                no_log=True,
                fallback=(env_fallback, ["LAUNCHDARKLY_SDK_KEY"]),
            ),
            overrides_flag=dict(type="list", elements="dict"),
            overrides_segment=dict(type="list", elem="dict"),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly-server-sdk"), exception=LD_IMP_ERR
        )

    headers = {"Authorization": module.params["sdk_key"]}
    resp = open_url(
        "https://app.launchdarkly.com/sdk/latest-all", headers=headers, method="GET"
    )

    test_data = json.loads(resp.read())
    if module.params.get("overrides_flag"):
        for k, v in [
            (k, v) for x in module.params["overrides_flag"] for (k, v) in x.items()
        ]:
            if v not in test_data["flags"][k]["variations"]:
                raise AnsibleError("Override variation does not match flag variations")

            if "flagValues" in test_data.keys():
                test_data["flagValues"][k] = v
            else:
                test_data["flagValues"] = {}
                test_data["flagValues"][k] = v
            del test_data["flags"][k]

    module.exit_json(changed=True, content=test_data)


if __name__ == "__main__":
    main()
