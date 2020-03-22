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
module: launchdarkly_feature_flag_validator
short_description: Validate Flags against Conftest OPA Policies written in Rego
description:
     - Validate Feature Flags in a Project
version_added: "0.3.0"
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

extends_documentation_fragment:
    - launchdarkly_labs.collection.launchdarkly
    - launchdarkly_labs.collection.launchdarkly_conftest
"""

EXAMPLES = r"""
# Get list of flags filtered to production environment.
- launchdarkly_feature_flag_info:
    api_key: api-12345
    project_key: dano-test-project
"""

RETURN = r"""
validated:
    description: If the policies were all successfully validated.
    type: bool
    returned: always
validation:
    description: List of Dictionaries, container flag key and list of failures as strings.
    returned: failure
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
    ld_common_argument_spec,
    rego_test,
)


def main():
    argument_spec = ld_common_argument_spec()
    argument_spec.update(
        dict(
            env=dict(type="str"),
            project_key=dict(type="str", required=True),
            tag=dict(type="str"),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    # Set up API
    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.FeatureFlagsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    feature_flags = _fetch_flags(module, api_instance)

    flags = feature_flags["items"]
    results = []
    for flag in flags:
        result = rego_test(module, flag)
        if result.results[0].failures:
            validation_fail = {"key": flag["key"], "failures": []}
            for failure in result.results[0].failures:
                validation_fail["failures"].append(failure["msg"])
            results.append(validation_fail)

    if results:
        module.exit_json(failed=True, validated=False, validation=results)
    else:
        module.exit_json(changed=True, validated=True)


def _fetch_flags(module, api_instance):
    try:
        if module.params.get("key"):
            if module.params.get("env"):
                response = api_instance.get_feature_flag(
                    module.params["project_key"],
                    module.params["key"],
                    env=module.params["env"],
                )
            else:
                response = api_instance.get_feature_flag(
                    module.params["project_key"], module.params["key"]
                )

        else:
            keys = ["project_key", "env", "summary", "archived", "tag"]
            filtered_keys = dict(
                (k, module.params[k])
                for k in keys
                if k in module.params and module.params[k] is not None
            )
            response = api_instance.get_feature_flags(**filtered_keys)

        return response.to_dict()
    except launchdarkly_api.rest.ApiException as e:
        if e.status == 404:
            return None
        else:
            fail_exit(module, e)


if __name__ == "__main__":
    main()
