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
module: launchdarkly_project
short_description: Create Project
description:
     - Manage LaunchDarkly Projects.
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the resource.
        choices: [ absent, present ]
        default: present
    api_key:
        description:
            - LaunchDarkly API Key. May be set as LAUNCHDARKLY_ACCESS_TOKEN environment variable.
        type: str
        required: yes
    project_key:
        description:
            - Project key will group flags together.
        default: 'default'
        required: yes
    name:
        description:
            - Display name for the environment.
        required: no
        type: str
    environments:
        description:
            - A list of Environments to create. Cannot be updated with this resource.
        type: str
    tags:
        description:
            - An array of tags for this project.
        required: no
        type: str
    include_in_snippet_by_default:
        description:
            - Whether or not all flags in project should be made available to the client-side JavaScript SDK.
        required: no
        type: bool
'''

EXAMPLES = r'''
# Create a new LaunchDarkly Environment
- project:
    state: present
    project_key: test-project-1
    color: C9C9C9
    tags:
      - dev
      - ops
      - frontend
    include_in_snippet_by_default: false
'''

RETURN = r'''
'''

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
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.environment import (
    ld_env_arg_spec,
    env_ld_builder,
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
            project_key=dict(type="str", required=True),
            name=dict(type="str", required_if=["state", "present"]),
            environments=dict(type="list", elements="dict", options=ld_env_arg_spec()),
            tags=dict(type="list", elements="str"),
            include_in_snippet_by_default=dict(type="bool"),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.ProjectsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    if module.params["environments"]:
        for env in module.params["environments"]:
            del env["environment_key"]

    if module.params["state"] == "present":
        project = _fetch_project(module, api_instance)
        if project:
            _configure_project(module, api_instance, project)
        else:
            _create_project(module, api_instance)
    elif module.params["state"] == "absent":
        _delete_project(module, api_instance)


def _parse_project_param(module, param_name, key=None):
    if key is None:
        key = launchdarkly_api.Project.attribute_map[param_name]
    path = "/" + key
    if param_name == "environments":
        value = env_ld_builder(module.params["environments"])
    else:
        value = module.params[param_name]
    return launchdarkly_api.PatchOperation(path=path, op="replace", value=value)


def _delete_project(module, api_instance):
    try:
        api_instance.delete_project(module.params["project_key"])
        module.exit_json(msg="successfully deleted project")
    except ApiException as e:
        err = json.loads(str(e.body))
        module.exit_json(msg=err)


def _create_project(module, api_instance):

    project_config = {
        "name": module.params["name"],
        "key": module.params["project_key"],
    }

    if module.params["environments"]:
        environments = []
        for env in module.params["environments"]:
            environments.append(env)
        project_config["environments"] = environments

    # if module.params['tags'] and module.params['tags'] is not None:
    #     project_config['tags'] = module.params['tags']

    # if module.params['include_in_snippet_by_default'] and module.params['include_in_snippet_by_default'] is not None:
    #     project_config['include_in_snippet_by_default'] = module.params['include_in_snippet_by_default']

    project_body = launchdarkly_api.ProjectBody(**project_config)

    try:
        response, status, headers = api_instance.post_project_with_http_info(
            project_body=project_body
        )
        module.exit_json(changed=True, content=response.to_dict())

    except ApiException as e:
        err = json.loads(str(e.body))
        module.exit_json(failed=True, changed=False, msg=err.message)


def _configure_project(module, api_instance, project=None, changed=False):
    patches = []

    if project:
        if module.params["tags"] is None or set(project.tags) == set(
            module.params["tags"]
        ):
            del module.params["tags"]
        if project.name == module.params["name"]:
            del module.params["name"]
        # Uncomment when attribute is added to project response
        # if project.include_in_snippet_by_default == module.params['include_in_snippet_by_default']:
        #    del module.parmas['include_in_snippet_by_default']

    for key in module.params:
        if module.params.get(key) and key not in [
            "state",
            "api_key",
            "environments",
            "project_key",
        ]:
            patches.append(_parse_project_param(module, key))

    if len(patches) > 0:
        try:
            response, status, headers = api_instance.patch_project_with_http_info(
                module.params["project_key"], patch_delta=patches
            )
            changed = True
        except ApiException as e:
            err = json.loads(str(e.body))
            module.exit_json(msg=err)

    try:
        response
    except NameError:
        response = project

    module.exit_json(
        changed=changed,
        msg="project successfully configured",
        content=response.to_dict(),
    )


def _fetch_project(module, api_instance):
    try:
        # Get an environment given a project and key.
        project = api_instance.get_project(module.params["project_key"])
        return project
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            err = json.loads(str(e.body))
            module.exit_json(msg=err)
    return False


if __name__ == "__main__":
    main()
