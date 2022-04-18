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
module: launchdarkly_user_segment
short_description: Manage user segments
description:
     - Manage LaunchDarkly user segments. To learn more, read L(Users and user segments, https://docs.launchdarkly.com/home/users).
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the Ansible resource
        choices: [ absent, present ]
        default: present
    project_key:
        description:
            - The project key
        default: 'default'
    environment_key:
        description:
            - The environment key
        required: yes
        type: str
    user_segment_key:
        description:
            - The user segment key
    name:
        description:
            - A human-readable name for the user segment
        required: yes
        type: str
    description:
        description:
            - A description for the user segment
        required: no
        type: str
    tags:
        description:
            - Manage a list of tags associated with the user segment
        required: no
        type: list
    included:
        description:
            - Manage a list of included users for the user segment
        required: no
        type: list
    excluded:
        description:
            - Manage a list of excluded users for the user segment
        required: no
        type: list

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Create a new LaunchDarkly user segment
- launchdarkly_user_segment:
    state: present
    project_key: test-project-1
    environment_key: test-environment-1
    user_segment_key: test-key-1
    name: "Test Segment"
    description: "This is a testing segment"
    rules:
        - clauses:
            - attribute: test-attribute
              op: contains
              values:
                - 2
                - 3
              negate: true
    tags:
      - blue
      - green
    included:
      - test1@example.com
      - test2@example.com
    excluded:
      - test3@example.com
      - test4@example.com
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
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.clause import (
    clause_argument_spec,
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    parse_user_param,
    fail_exit,
    ld_common_argument_spec,
    rego_test,
)


def usr_argument_spec():
    return dict(
        type="list",
        elements="dict",
        options=dict(
            weight=dict(type="int"),
            bucket_by=dict(type="str"),
            clauses=clause_argument_spec(),
        ),
    )


def main():
    argument_spec = ld_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(type="str", default="present", choices=["absent", "present"]),
            environment_key=dict(type="str", required=True),
            project_key=dict(type="str", required=True),
            user_segment_key=dict(type="str", required=True),
            name=dict(type="str"),
            description=dict(type="str"),
            tags=dict(type="list"),
            included=dict(type="list"),
            excluded=dict(type="list"),
            rules=usr_argument_spec(),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.UserSegmentsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    if module.params["state"] == "present":
        user_segment = _fetch_user_segment(module, api_instance)
        if user_segment:
            _configure_user_segment(module, api_instance, user_segment)
        else:
            _create_user_segment(module, api_instance)
    elif module.params["state"] == "absent":
        _delete_user_segment(module, api_instance)


def _delete_user_segment(module, api_instance):
    try:
        api_instance.delete_user_segment(
            module.params["project_key"],
            module.params["environment_key"],
            module.params["user_segment_key"],
        )
        module.exit_json(changed=True, msg="successfully deleted user segment")
    except ApiException as e:
        fail_exit(module, e)


def _create_user_segment(module, api_instance):
    if module.params["conftest"]["enabled"]:
        rego_test(module)

    name = (
        module.params["name"]
        if module.params["name"] is not None
        else module.params["user_segment_key"]
    )
    user_segment_config = {"name": name, "key": module.params["user_segment_key"]}

    user_segment_config["description"] = (
        module.params["description"] if module.params.get("description") else ""
    )
    user_segment_config["tags"] = (
        module.params["tags"] if module.params.get("tags") else []
    )

    user_segment_body = launchdarkly_api.UserSegmentBody(**user_segment_config)

    try:
        api_response = api_instance.post_user_segment(
            module.params["project_key"],
            module.params["environment_key"],
            user_segment_body,
        )
    except ApiException as e:
        fail_exit(module, e)

    _configure_user_segment(module, api_instance, api_response, True)


def _configure_user_segment(module, api_instance, api_response=None, ans_changed=False):
    name = (
        module.params["name"]
        if module.params["name"] is not None
        else module.params["user_segment_key"]
    )
    patches = []
    user_segment = api_response
    if user_segment:
        if user_segment.name == name and module.params["name"]:
            del module.params["name"]
        if (
            user_segment.description == module.params["description"]
            and module.params["description"]
        ):
            del module.params["description"]
        if set(user_segment.tags) == set(module.params["tags"]):
            del module.params["tags"]
        if (
            user_segment.included
            and module.params["included"]
            and set(user_segment.included) == set(module.params["included"])
        ):
            del module.params["included"]
        if (
            user_segment.excluded
            and module.params["excluded"]
            and set(user_segment.excluded) == set(module.params["excluded"])
        ):
            del module.params["excluded"]
        dict_segment = user_segment.to_dict()
        result = diff(
            dict_segment["rules"],
            module.params["rules"],
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
                    "user_segment_key",
                    "conftest",
                ]
            ),
        )
        if len(list(result)) == 0:
            del module.params["rules"]
    for key in module.params:
        if key not in [
            "state",
            "api_key",
            "environment_key",
            "project_key",
            "user_segment_key",
            "conftest",
        ]:
            if module.params[key] is not None:
                patches.append(parse_user_param(module.params, key))

    if len(patches) > 0:
        try:
            response, status, headers = api_instance.patch_user_segment_with_http_info(
                module.params["project_key"],
                module.params["environment_key"],
                module.params["user_segment_key"],
                patch_only=patches,
            )
            ans_changed = True
            segment = response
            msg = "user segment successfully configured"
        except ApiException as e:
            if e.status == 404:
                module.exit_json(failed=True, msg="user segment key not found")
            else:
                fail_exit(module, e)
    else:
        segment = user_segment
        msg = "segment unchanged"

    module.exit_json(
        changed=ans_changed, msg=msg, user_segment=to_native(segment.to_dict())
    )


def _fetch_user_segment(module, api_instance):
    try:
        # Get a user segment given a project, environment, and user_segment_key.
        user_segment = api_instance.get_user_segment(
            module.params["project_key"],
            module.params["environment_key"],
            module.params["user_segment_key"],
        )
        return user_segment
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            fail_exit(module, e)
    return False


if __name__ == "__main__":
    main()
