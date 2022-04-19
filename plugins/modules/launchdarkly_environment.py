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
module: launchdarkly_environment
short_description: Manage environments
description:
     - Manage LaunchDarkly environments for a given project. To learn more, read L(Environments, https://docs.launchdarkly.com/home/organize/environments).
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the Ansible resource
        choices: [ absent, present ]
        default: present
        type: str
    project_key:
        description:
            - The project key
        default: 'default'
    environment_key:
        description:
            - The environment key. Must be unique within this project.
        required: yes
        type: str©
    name:
        description:
            - A human-readable name for the environment
        type: str
    color:
        description:
            - The color to indicate this environment in the LaunchDarkly UI
        required: no
        type: str
    default_ttl:
        description:
            - The default time (in minutes) that the PHP SDK can cache feature flag rules locally
        type: int
    secure_mode:
        description:
            - Ensures that a user of the client-side SDK cannot impersonate another user
    default_track_events:
        description:
            - Enables tracking detailed information for new flags by default
        type: bool
    tags:
        description:
            - An array of tags to apply to this environment
        type: str
    require_comments:
        description:
            - Requires comments for all flag and segment changes through the UI in this environment
        type: bool
    confirm_changes:
        description:
            - Requires confirmation for all flag and segment changes through the UI in this environment
        type: bool

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
---
# Create a new LaunchDarkly environment
- launchdarkly_environment:
    state: present
    project_key: test-project-1
    environment_key: test-environment-1
    color: C9C9C9

# Create a new LaunchDarkly environment and tag it
- launchdarkly_environment:
    state: present
    project_key: test-project-1
    environment_key: test-environment-1
    color: C9C9C9
    tags:
      - blue
      - green

"""

RETURN = r"""
environment:
    description: Dictionary containing an L(environment, https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/Environment.md)
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
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    parse_env_param,
    fail_exit,
    ld_common_argument_spec,
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.environment import (
    ld_env_arg_spec,
    env_ld_builder,
)


def main():
    mutually_exclusive = []
    spec = ld_common_argument_spec()
    spec.update(ld_env_arg_spec())
    spec.update(
        dict(
            state=dict(type="str", default="present", choices=["absent", "present"]),
            api_key=dict(
                required=True,
                type="str",
                no_log=True,
                fallback=(env_fallback, ["LAUNCHDARKLY_ACCESS_TOKEN"]),
            ),
            project_key=dict(type="str", required=True),
            secure_mode=dict(type="bool"),
            require_comments=dict(type="bool"),
            confirm_changes=dict(type="bool"),
            default_track_events=dict(type="bool"),
            tags=dict(type="list", elements="str"),
        )
    )

    module = AnsibleModule(argument_spec=spec, mutually_exclusive=mutually_exclusive)

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.EnvironmentsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    if module.params["state"] == "present":
        environment = _fetch_environment(module, api_instance)
        if environment:
            _configure_environment(module, api_instance, environment)
        else:
            _create_environment(module, api_instance)
    elif module.params["state"] == "absent":
        _delete_environment(module, api_instance)


def _delete_environment(module, api_instance):
    try:
        response, status, headers = api_instance.delete_environment_with_http_info(
            module.params["project_key"], module.params["environment_key"]
        )
        if status != 204:
            module.exit_json(
                failed=True, msg="Failed to delete enviroment status: %d" % status
            )
        module.exit_json(msg="successfully deleted environment")
    except ApiException as e:
        fail_exit(module, e)


def _create_environment(module, api_instance):

    environment_config = {
        "name": module.params["name"],
        "key": module.params["environment_key"],
        "color": module.params["color"],
    }

    if module.params["default_ttl"]:
        environment_config["defaultTtl"] = module.params["default_ttl"]
    environment_body = launchdarkly_api.EnvironmentPost(**environment_config)

    try:
        _, status, _ = api_instance.post_environment_with_http_info(
            project_key=module.params["project_key"], environment_body=environment_body
        )
        if status != 201:
            module.exit_json(
                failed=True, msg="failed to create environment, status: %d" % status
            )
    except ApiException as e:
        fail_exit(module, e)

    _configure_environment(module, api_instance)


def _configure_environment(module, api_instance, environment=None):
    changed = False
    patches = []
    if environment:
        if environment.name == module.params["name"]:
            del module.params["name"]
        if environment.color == module.params["color"]:
            del module.params["color"]
        if (
            environment.default_ttl == module.params["default_ttl"]
            or module.params["default_ttl"] is None
        ):
            del module.params["default_ttl"]
        if environment.secure_mode == module.params["secure_mode"]:
            del module.params["secure_mode"]
        if environment.default_track_events == module.params["default_track_events"]:
            del module.params["default_track_events"]
        if set(environment.tags) == set(module.params["tags"]):
            del module.params["tags"]
        if environment.confirm_changes == module.params["confirm_changes"]:
            del module.params["confirm_changes"]
        if environment.require_comments == module.params["require_comments"]:
            del module.params["require_comments"]
        if len(module.params.keys()) <= 4:
            module.exit_json(changed=False, msg="environment unchanged")
    for key in module.params:
        if (
            key
            not in ["state", "api_key", "environment_key", "project_key", "conftest"]
            and module.params[key] is not None
        ):
            patches.append(parse_env_param(module.params, key))

    if len(patches) > 0:
        try:
            api_response = api_instance.patch_environment(
                module.params["project_key"],
                module.params["environment_key"],
                patch_delta=patches,
            )
        except ApiException as e:
            fail_exit(module, e)

        module.exit_json(
            changed=True,
            msg="environment successfully configured",
            environment=api_response.to_dict(),
        )

    module.exit_json(
        changed=False, msg="environment unchanged", environment=environment.to_dict()
    )


def _fetch_environment(module, api_instance):
    try:
        # Get an environment given a project and key.
        environment = api_instance.get_environment(
            module.params["project_key"], module.params["environment_key"]
        )
        return environment
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            fail_exit(module, e)
    return False


if __name__ == "__main__":
    main()
