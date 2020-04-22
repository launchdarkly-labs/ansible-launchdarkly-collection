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
module: launchdarkly_project_info
short_description: Return a single Project
description:
     - Return a dictionary of a single LaunchDarkly Project
version_added: "0.2.11"
options:
    project_key:
        description:
            - Project key will group flags together
        default: 'default'
        required: yes

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Get list of flags filtered to production environment.
- launchdarkly_project_info:
    api_key: api-12345
    project_key: dano-test-project
"""

RETURN = r"""
project:
    description: Dictionary containing a L(Project, https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/Project.md)
    type: dict
    returned: on success
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
            project_key=dict(type="str", required=False),
            tags=dict(type="list", required=False),
            environment_tags=dict(type="list", required=False),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    # Set up API
    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.ProjectsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    project = _fetch_projects(module, api_instance)

    module.exit_json(changed=True, project=project)


def _fetch_projects(module, api_instance):
    try:
        if module.params.get("project_key"):
            response = api_instance.get_project(module.params["project_key"]).to_dict()

        else:
            get_projects = api_instance.get_projects()
            if module.params.get("tags"):
                projects = [proj.to_dict() for proj in get_projects.items]
                filter_projects = [
                    d
                    for d in projects
                    if len(set(d["tags"]).intersection(module.params["tags"]))
                ]
                final_projects = []
                for i, proj in enumerate(filter_projects):
                    filtered_environments = []
                    for env in proj["environments"]:
                        if module.params.get("environment_tags") and set(
                            env["tags"]
                        ).intersection(module.params["environment_tags"]):
                            filtered_environments.append(env)
                        elif module.params.get("environment_tags"):
                            continue
                        else:
                            filtered_environments = env
                    filter_projects[i]["environments"] = filtered_environments
                    final_projects.append(filter_projects)
                get_projects = [
                    d for d in filter_projects if len(d["environments"]) > 0
                ]

            response = get_projects

        return response
    except launchdarkly_api.rest.ApiException as e:
        if e.status == 404:
            return None
        else:
            fail_exit(module, e)


if __name__ == "__main__":
    main()
