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
module: launchdarkly_project_copy
short_description: Copy source LaunchDarkly Project in or between accounts.
description:
     - Copy source LaunchDarkly Project in or between accounts. This can be used to make a clone of an existing project.
version_added: "0.2.2"
options:
    api_key:
        description:
            - LaunchDarkly API Source Key. May be set as LAUNCHDARKLY_ACCESS_TOKEN environment variable.
        type: str
        required: yes
    backup_path:
        description:
            - Reads in a LaunchDarkly snapshot files and replays against API.
        type: str
        required: yes

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
# Sync a LaunchDarkly Project
- launchdarkly_restore:
    api_key: api-12345
    backup_path: "./"
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
    from launchdarkly_api.rest import ApiException

    # from dictdiffer import diff

    HAS_LD = True
except ImportError:
    LD_IMP_ERR = traceback.format_exc()
    HAS_LD = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback
from ansible.module_utils._text import to_native
from ansible.module_utils.common._json_compat import json

# from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
#     configure_instance,
#     parse_env_param,
#     parse_user_param,
#     reset_rate,
#     fail_exit,
#     ld_common_argument_spec,
# )

from base import (
    configure_instance,
    parse_env_param,
    parse_user_param,
    reset_rate,
    fail_exit,
    ld_common_argument_spec,
)

from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.flag import (
    configure_defaults,
    configure_clientside_avail
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
            project_key=dict(
                required=True,
                type="str",
            ),
            backup_path=dict(
                required=True,
                type="str",
            ),
        )
    )

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    api_instance_dest_user = launchdarkly_api.UserSegmentsApi(
        launchdarkly_api.ApiClient(configure_instance(module.params["api_key"]))
    )

    api_instance_dest_proj = launchdarkly_api.ProjectsApi(
        launchdarkly_api.ApiClient(configure_instance(module.params["api_key"]))
    )

    api_instance_dest_fflag = launchdarkly_api.FeatureFlagsApi(
        launchdarkly_api.ApiClient(configure_instance(module.params["api_key"]))
    )

    api_instance_dest_env = launchdarkly_api.EnvironmentsApi(
        launchdarkly_api.ApiClient(configure_instance(module.params["api_key"]))
    )

    _project_restore(
        module,
        api_instance_dest_proj,
        api_instance_dest_env,
        api_instance_dest_fflag,
        api_instance_dest_user,
    )


def _project_restore(module, dest_proj, dest_env_api, dest_fflags, dest_user_sgmt):
    with open(module.params["backup_path"]) as reader:
        backup_json = json.load(reader)

    project = backup_json["project"]
    feature_flags = backup_json["feature_flags"]
    segments = backup_json["segments"]

    name = project.get("name", "")
    dest_proj_body = dict(
        name=name, key=module.params["project_key"], tags=project["tags"]
    )

    patch_envs = []
    # Build the Environments inside of Project Body
    if project["environments"]:
        dest_proj_body["environments"] = []
        for env in project["environments"]:
            dest_proj_body["environments"].append(
                dict(
                    name=env["name"],
                    key=env["key"],
                    color=env["color"],
                    default_ttl=env["default_ttl"],
                )
            )

            patch_env = dict(key=env["key"])
            if env["tags"]:
                patch_env["tags"] = env["tags"]

            if env["secure_mode"] is not False:
                patch_env["secure_mode"] = env["secure_mode"]

            if env["default_track_events"] is not False:
                patch_env["default_track_events"] = env["default_track_events"]

            if env["require_comments"] is not False:
                patch_env["require_comments"] = env["require_comments"]

            if env["confirm_changes"] is not False:
                patch_env["confirm_changes"] = env["confirm_changes"]

            patch_envs.append(patch_env)

    ld_proj = launchdarkly_api.ProjectBody(**dest_proj_body)

    try:
        response, status, headers = dest_proj.post_project_with_http_info(
            project_body=ld_proj
        )

    except ApiException as e:
        fail_exit(module, e)

    # Project Environment Processing
    patches = []
    for env in patch_envs:
        for key in env:
            if key not in ["key"] and env[key] is not None:
                patches.append(parse_env_param(env, key))

        if len(patches) > 0:
            try:
                api_response = dest_env_api.patch_environment(
                    module.params["project_key"], env["key"], patch_delta=patches
                )
            except ApiException as e:
                if status == 429:
                    time.sleep(reset_rate(headers["X-RateLimit-Reset"]))
                    # Retry
                    dest_env_api.patch_environment(
                        module.params["project_key"],
                        env["key"],
                        patch_delta=patches,
                    )
                else:
                    fail_exit(module, e)
            # Reset patches
            patches = []

    # User Segment Processing
    if segments:
        env_keys = segments.keys()
        for env in env_keys:
            patch_sgmts = []
            for segment in segments[env]:
                new_segment_body = dict(key=segment["key"], name=segment["name"])

                if segment["description"]:
                    new_segment_body["description"] = segment["description"]

                if segment["tags"]:
                    new_segment_body["tags"] = segment["tags"]
                try:
                    dest_user_sgmt.post_user_segment(
                        module.params["project_key"], env, new_segment_body
                    )
                except ApiException as e:
                    if status == 429:
                        time.sleep(reset_rate(headers["X-RateLimit-Reset"]))
                        # Retry
                        dest_user_sgmt.post_user_segment(
                            module.params["project_key"],
                            env,
                            new_segment_body,
                        )
                    else:
                        fail_exit(module, e)

                patch_sgmt = dict(key=segment["key"])
                if segment["included"] is not None:
                    patch_sgmt["included"] = segment["included"]

                if segment["excluded"] is not None:
                    patch_sgmt["excluded"] = segment["excluded"]

                if segment["rules"] is not None:
                    patch_sgmt["rules"] = segment["rules"]

                patch_sgmts.append(patch_sgmt)

            for sgmt in patch_sgmts:
                patches = []
                for key in sgmt:
                    if key not in ["key"] and len(sgmt[key]) > 0:
                        if key == "rules":
                            for rule in sgmt["rules"]:
                                patch = dict(
                                    path="/rules/-",
                                    op="add",
                                    value=launchdarkly_api.UserSegmentRule(**rule),
                                )
                                patches.append(launchdarkly_api.PatchOperation(**patch))
                                del patch
                        else:
                            patches.append(parse_user_param(sgmt, key))
                if len(patches) > 0:
                    try:
                        (
                            response,
                            status,
                            headers,
                        ) = dest_user_sgmt.patch_user_segment_with_http_info(
                            module.params["project_key"],
                            env,
                            sgmt["key"],
                            patch_only=patches,
                        )

                    except ApiException as e:
                        if status == 429:
                            time.sleep(reset_rate(headers["X-RateLimit-Reset"]))
                            # Retry
                            dest_user_sgmt.patch_user_segment_with_http_info(
                                module.params["project_key"],
                                env,
                                sgmt["key"],
                                patch_only=patches,
                            )
                        else:
                            fail_exit(module, e)
                # Reset patches
                del patches

    for flag in feature_flags:
        fflag_body = dict(
            name=flag["name"],
            key=flag["key"],
            description=flag["description"],
            variations=flag["variations"],
            temporary=flag["temporary"],
            tags=flag["tags"],
        )

        fflag_body = configure_defaults(fflag_body, flag)
        fflag_body = configure_clientside_avail(fflag_body, flag)


        fflag_body_mapped = dict(
            (launchdarkly_api.FeatureFlagBody.attribute_map[k], v)
            for k, v in fflag_body.items()
            if v is not None
        )

        try:
            response, status, headers = dest_fflags.post_feature_flag_with_http_info(
                module.params["project_key"], fflag_body_mapped
            )
        except ApiException as e:
            if e.status == 429:
                time.sleep(reset_rate(headers["X-RateLimit-Reset"]))
                # Retry
                (
                    response,
                    status,
                    headers,
                ) = dest_fflags.post_feature_flag_with_http_info(
                    module.params["project_key"], fflag_body
                )
            else:
                fail_exit(module, e)

        for fenv_key in flag["environments"]:
            patches = []

            fflag_env = dict(
                on=flag["environments"][fenv_key]["on"],
                targets=flag["environments"][fenv_key]["targets"],
                off_variation=flag["environments"][fenv_key]["off_variation"],
                track_events=flag["environments"][fenv_key]["track_events"],
                prerequisites=flag["environments"][fenv_key]["prerequisites"],
                fallthrough=flag["environments"][fenv_key]["fallthrough"],
            )

            fflag_env_mapped = dict(
                (launchdarkly_api.FeatureFlagConfig.attribute_map[k], v)
                for k, v in fflag_env.items()
                if v is not None
            )
            path = "/environments/" + fenv_key + "/"
            for key in fflag_env_mapped:
                if fflag_env_mapped.get(key) is not None:
                    patch = dict(
                        path=path + key, op="replace", value=fflag_env_mapped[key]
                    )
                    patches.append(launchdarkly_api.PatchOperation(**patch))
                    del patch
            try:
                if flag["environments"][fenv_key]["rules"] is not None:
                    for rule in flag["environments"][fenv_key]["rules"]:
                        new_rule = dict(clauses=rule["clauses"])

                        if rule["rollout"] is not None:
                            new_rule["rollout"] = rule["rollout"]
                        if rule["variation"] is not None:
                            new_rule["variation"] = rule["variation"]

                        patch = dict(
                            path=path + "rules/-",
                            op="add",
                            value=launchdarkly_api.Rule(**new_rule),
                        )
                        patches.append(launchdarkly_api.PatchOperation(**patch))
            except KeyError:
                pass

            if len(patches) > 0:
                try:
                    (
                        response,
                        status,
                        headers,
                    ) = dest_fflags.patch_feature_flag_with_http_info(
                        project["key"],
                        flag["key"],
                        patch_comment=patches,
                    )

                except ApiException as e:
                    if e.status == 429:
                        time.sleep(reset_rate(headers["X-RateLimit-Reset"]))
                        # Retry
                        dest_fflags.patch_feature_flag_with_http_info(
                            module.params["project_key_dest"],
                            flag["key"],
                            patch_comment=patches,
                        )
                    else:
                        fail_exit(module, e)
                # Reset patches
                del patches

    new_project = dest_proj.get_project(project["key"]).to_dict()
    module.exit_json(
        changed=True,
        project=new_project,
        msg="Restored project: %s" % module.params["project_key"],
    )


if __name__ == "__main__":
    main()
