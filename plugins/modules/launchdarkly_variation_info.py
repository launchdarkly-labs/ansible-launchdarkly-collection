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
module: launchdarkly_variation_info
short_description: Return the value from a feature flag evaluation
description:
     - Return the value from a LaunchDarkly feature flag evaluation. To learn more, read L(Evaluating flags, https://docs.launchdarkly.com/sdk/features/evaluating).
version_added: "0.2.0"
options:
    sdk_key:
        description:
            - The SDK key for the environment where the flag evaluation occurs. You may also set this in the C(LAUNCHDARKLY_SDK_KEY) environment variable.
        default: 'default'
        required: yes
        type: str
    start_wait:
        description:
            - How long to wait for the SDK to connect to LaunchDarkly
        default: 5
        required: yes
        type: int
    flag_key:
        description:
            - The feature flag key
        required: no
        type: str
    user:
        description:
            - The user for whom the flag is being evaluated. Must include the user C(key). May also include a dictionary of C(custom) user attributes, illustrated in the example below.
        required: no
        type: dict
"""

EXAMPLES = r"""
# Return the value from a feature flag evaluation
- launchdarkly_variation_info:
    sdk_key: sdk-12345
    start_wait: 10
    flag_key: example-test-flag
    user:
        key: aabbccdd
        custom:
            test-attribute: green
            plan: free
"""

RETURN = r"""
type:
    description: Type of return value
    type: string
    returned: always
value:
    description: Value returned from variation. Type is set in C(type) return.
    returned: always
variation_index:
    description: Index value of variation
    type: int
    returned: always
reason:
    description: Describes why the value was returned. To learn more, read L(Flag evaluation reasons, https://docs.launchdarkly.com/sdk/features/evaluation-reasons).
    type: dict
    returned: always
is_default_value:
    description: Whether the returned value is the default, or fallback, value provided as part of the evaluation request.
    type: bool
    returned: always
"""

import inspect
import traceback
import time

LD_IMP_ERR = None
try:
    import ldclient

    HAS_LD = True
except ImportError:
    LD_IMP_ERR = traceback.format_exc()
    HAS_LD = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback
from ansible.module_utils._text import to_native
from ansible.module_utils.common._json_compat import json
from ansible.module_utils.six import PY2, iteritems, string_types
from ansible.errors import AnsibleError


def main():
    module = AnsibleModule(
        argument_spec=dict(
            sdk_key=dict(
                required=True,
                type="str",
                no_log=True,
                fallback=(env_fallback, ["LAUNCHDARKLY_SDK_KEY"]),
            ),
            flag_key=dict(type="str", required=True),
            user=dict(type="dict", required=True),
            start_wait=dict(type="int", default=5),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly-server-sdk"), exception=LD_IMP_ERR
        )

    ldclient.set_sdk_key(module.params["sdk_key"])
    ldclient.start_wait = 5
    ld_client = ldclient.get()

    if not ld_client.is_initialized():
        raise AnsibleError("Error: Not Connected to LaunchDarkly")

    show_feature = ld_client.variation_detail(
        module.params["flag_key"], module.params["user"], False
    )

    ld_client.flush()

    ff_type = type(show_feature.value).__name__
    value = show_feature.value
    ld_client.close()

    if ff_type == "dict":
        ff_end_type = "json"
    elif ff_type == "unicode":
        ff_end_type = "string"
    elif ff_type == "int":
        ff_end_type = "number"
    elif ff_type == "bool":
        ff_end_type = "bool"

    module.exit_json(
        type=ff_end_type,
        value=show_feature.value,
        variation_index=show_feature.variation_index,
        reason=show_feature.reason,
        is_default_value=show_feature.is_default_value(),
    )


if __name__ == "__main__":
    main()
