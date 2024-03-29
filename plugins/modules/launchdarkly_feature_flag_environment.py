#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "0.1.0",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
module: launchdarkly_feature_flag_environment
short_description: Configure feature flag targeting
description:
     - Configure LaunchDarkly feature flag targeting for a given flag in a specific environment and project. To learn more, read L(Targeting users with flags, https://docs.launchdarkly.com/home/flags/targeting-users).
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the Ansible resource
        choices: [ absent, enabled, disabled, present ]
        default: present
        type: str
    api_key:
        description:
            - LaunchDarkly API access token. You may also set this in the C(LAUNCHDARKLY_ACCESS_TOKEN) environment variable.
        type: str
        required: yes
    project_key:
        description:
            - The project key
        default: 'default'
    environment_key:
        description:
            - The environment key
        required: yes
        type: str
    off_variation:
        description:
            - Variation served if flag targeting is turned off
        type: int
    targets:
        description:
            - Target individual users by assigning them to a specific variation
        type: list
        suboptions:
            variation:
                description:
                    - Index of variation to serve default. Exclusive of rollout.
                type: int
            values:
                description:
                    - Individual users to target with this variation
            state:
                choices: [ absent, add, remove, replace ]
                default: replace
                description:
                    - Indicate desired state of the particular variation
    rules:
        description:
            - Target users based on user attributes. This is a nested dictionary describing the variations to serve, illustrated in the example below.
        type: list
    fallthrough:
        description:
            - Nested dictionary describing the default variation to serve if no C(prerequisites),
            - C(targets), or C(rules) apply
        suboptions:
            variation:
                description:
                    - Index of variation to serve default. Exclusive of rollout.
                type: int
            rollout:
                description:
                    - Rollout value
                type: dict

extends_documentation_fragment: launchdarkly_labs.collection.launchdarkly
"""

EXAMPLES = r"""
---
# Configure a feature flag within an environment
- launchdarkly_feature_flag_environment:
    state: present
    flag_key: example_flag
    environment_key: default
    off_variation: 1
    targets:
        - variation: 1
          values:
            - test@example.com
            - test2@example.com
    comment: Updating default env values

- launchdarkly_feature_flag_environment:
    state: enabled
    flag_key: example_2
    environment_key: env_2
    fallthrough:
      variation: 1
    rules:
    - variation: 1
        clauses:
        - attribute: test-attribute
            op: contains
            values:
            - 2
            - 3
            negate: true
    prerequisites:
      - variation: 0
        key: example_flag
"""

RETURN = r"""
---
feature_flag_environment:
    description: Dictionary containing a L(Feature Flag Config, https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/FeatureFlagConfig.md)
    type: dict
    returned: on success
"""

import traceback
import copy


LD_IMP_ERR = None
try:
    import launchdarkly_api
    from launchdarkly_api.rest import ApiException
    from dictdiffer import diff

    HAS_LD = True
except ImportError:
    LD_IMP_ERR = traceback.format_exc()
    HAS_LD = False

from ansible.errors import AnsibleError
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native
from ansible.module_utils.common._json_compat import json

from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    _patch_path,
    _patch_op,
    _build_comment,
    fail_exit,
    ld_common_argument_spec,
    rego_test,
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.rule import (
    rule_argument_spec,
)


def main():
    argument_spec = ld_common_argument_spec()
    argument_spec.update(
        dict(
            state=dict(
                type="str",
                default="present",
                choices=["absent", "present", "enabled", "disabled"],
            ),
            flag_key=dict(type="str", required=True),
            environment_key=dict(type="str", required=True),
            project_key=dict(type="str", required=True),
            off_variation=dict(type="int"),
            track_events=dict(type="bool"),
            comment=dict(type="str"),
            salt=dict(type="str"),
            targets=dict(
                type="list",
                elements="dict",
                options=dict(
                    values=dict(type="list"),
                    variation=dict(type="int"),
                    state=dict(
                        type="str",
                        default="replace",
                        choices=["add", "remove", "replace", "absent"],
                    ),
                ),
            ),
            fallthrough=dict(
                type="dict",
                options=dict(
                    variation=dict(type="int"),
                    rollout=dict(
                        type="dict",
                        # elements="dict",
                        bucket_by=dict(type="str"),
                        weighted_variations=dict(
                            type="list",
                            elements="dict",
                            options=dict(
                                variation=dict(type="int"), weight=dict(type="int")
                            ),
                        ),
                    ),
                ),
            ),
            rules=rule_argument_spec(),
            prerequisites=dict(
                type="list",
                options=dict(key=dict(type="str"), variation=dict(type="int")),
            ),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_LD:
        module.fail_json(
            msg=missing_required_lib("launchdarkly_api"), exception=LD_IMP_ERR
        )

    configuration = configure_instance(module.params["api_key"])
    api_instance = launchdarkly_api.FeatureFlagsApi(
        launchdarkly_api.ApiClient(configuration)
    )

    if module.params["state"] == "absent":
        _delete_feature_flag_env(module, api_instance)
    else:
        feature_flag = _fetch_feature_flag(module, api_instance)
        _configure_feature_flag_env(module, api_instance, feature_flag)


def _toggle_flag(state, patches, feature_flag, env):
    if state == "enabled":
        value = True
    elif state == "disabled":
        value = False
    else:
        value = feature_flag.on

    if feature_flag.on != value:
        path = _patch_path(env, "on")
        patches.append(
            launchdarkly_api.PatchOperation(path=path, op="replace", value=value)
        )

    return patches


def _parse_flag_param(params, env, key, op="replace"):
    path = _patch_path(env, launchdarkly_api.FeatureFlagConfig.attribute_map[key])

    return launchdarkly_api.PatchOperation(path=path, op=op, value=params[key])


def configure_feature_flag_env(params, feature_flag):
    env = params["environment_key"]
    patches = []
    clauses_list = []

    _toggle_flag(params["state"], patches, feature_flag, env)

    if (
        feature_flag.off_variation == params["off_variation"]
        or params.get("off_variation") is None
    ):
        del params["off_variation"]

    if (
        feature_flag.track_events == params["track_events"]
        or params.get("track_events") is None
    ):
        del params["track_events"]

    # Loop over prerequisites comparing
    _check_prereqs(params["prerequisites"], feature_flag)
    # Loop over targets comparing
    if params["targets"] is not None:
        flag_var_index = {}
        # Map variation to index flag targets first:
        for idx, target in enumerate(feature_flag.targets):
            target_dict = target.to_dict()
            target_index = str(target_dict["variation"])
            wtf = str(idx)
            flag_var_index = {
                target_dict["variation"]: {
                    "index": wtf,
                    "targets": target_dict["values"],
                }
            }

        # Check if targets already exist in variation
        for target in params["targets"]:
            if target["state"] == "add":
                if flag_var_index:
                    if set(target["values"]).issubset(
                        set(flag_var_index[target["variation"]]["targets"])
                    ):
                        continue
                    else:
                        new_targets = list(
                            set(target["values"])
                            - set(flag_var_index[target["variation"]]["targets"])
                        )
                        target_index = str(flag_var_index[target["variation"]]["index"])
                        new_targets_idx = len(
                            flag_var_index[target["variation"]]["targets"]
                        )
                        for val_idx, val in enumerate(new_targets):
                            new_idx = str(new_targets_idx + val_idx)
                            path = (
                                _patch_path(env, "targets")
                                + "/"
                                + target_index
                                + "/values/"
                                + new_idx
                            )
                            patches.append(_patch_op("add", path, new_targets[val_idx]))
                        continue

                else:
                    new_targets = set(target["values"])
                    target_index = "0"
                    val_index = "0"

            elif target["state"] == "replace":
                if flag_var_index:
                    if set(target["values"]) == set(
                        flag_var_index[target["variation"]]["targets"]
                    ):
                        continue
                    else:
                        new_targets = set(target["values"])
                        target_index = str(flag_var_index[target["variation"]]["index"])
                        val_index = str(flag_var_index[target["variation"]]["index"])
                else:
                    new_targets = set(target["values"])
                    target_index = "0"
                    # Replace does not work on empty targets
                    target["state"] = "add"

            elif target["state"] == "remove":
                if set(target["values"]).issubset(
                    set(flag_var_index[target["variation"]]["targets"])
                ):
                    new_targets = set(target["values"])
                    target_index = str(flag_var_index[target["variation"]]["index"])
                    val_index = str(flag_var_index[target["variation"]]["index"])
                else:
                    raise AnsibleError("Targets not found")

            elif target["state"] == "absent":
                try:
                    target_index = str(flag_var_index[target["variation"]]["index"])
                    path = _patch_path(env, "targets") + "/" + target_index
                    patches.append(dict(op="remove", path=path))
                except KeyError:
                    pass
                continue

            path = _patch_path(env, "targets") + "/" + target_index
            patches.append(
                _patch_op(
                    target["state"],
                    path,
                    {"variation": target["variation"], "values": list(new_targets)},
                )
            )

        del params["targets"]

    # Loop over rules comparing
    if params["rules"] is not None:
        rule_patches, rule_clauses = _process_rules(params["rules"], feature_flag, env)
        del params["rules"]
        patches.extend(rule_patches)
        clauses_list.extend(rule_clauses)
    # Compare fallthrough
    fallthrough = diff(
        params["fallthrough"],
        feature_flag.fallthrough.to_dict(),
        ignore=set(["id"]),
    )
    if not list(fallthrough):
        del params["fallthrough"]
    else:
        fallthrough = _build_rules(params["fallthrough"])
        op = "replace"
        path = _patch_path(env, "fallthrough")
        patches.append(_patch_op(op, path, fallthrough))
        # Delete key so it's not passed through to next loop
        del params["fallthrough"]

    for key in params:
        if (
            key
            not in [
                "state",
                "api_key",
                "environment_key",
                "project_key",
                "flag_key",
                "comment",
                "salt",
                "conftest",
            ]
            and params[key] is not None
        ):
            patches.append(_parse_flag_param(params, env, key))

    return patches, clauses_list


def _configure_feature_flag_env(module, api_instance, feature_flag=None):
    if module.params["conftest"]["enabled"]:
        rego_test(module)

    patches, clauses_list = configure_feature_flag_env(module.params, feature_flag)

    if patches:
        comments = dict(comment=_build_comment(module), patch=patches)
        try:
            api_response = api_instance.patch_feature_flag(
                module.params["project_key"],
                module.params["flag_key"],
                patch_comment=comments,
            )
        except Exception as e:
            raise AnsibleError("Error applying configuration: %s" % to_native(e))
        output_patches = []
        for patch in patches:
            if type(patch) is dict:
                output_patches.append(patch)
            else:
                output_patches.append(patch.to_dict())
        module.exit_json(
            changed=True,
            msg="flag environment successfully configured",
            feature_flag_environment=api_response.to_dict(),
            patches=output_patches,
            clauses=clauses_list,
        )

    module.exit_json(
        changed=False,
        msg="flag environment unchanged",
        feature_flag_environment=feature_flag.to_dict(),
    )


def _process_rules(rules, feature_flag, env):
    patches = []
    clauses_list = []
    old_rules = max(len(feature_flag.rules) - 1, 0)
    new_index = max(len(rules) - 1, 0)
    # Make copy for next step.
    new_rules_copy = copy.deepcopy(rules)
    flag_index = 0

    for new_rule_index, rule in enumerate(rules):
        state = rule.get("rule_state", "present")
        if rule.get("rule_state"):
            del rule["rule_state"]

        # Trim old rules, if state isn't add
        if new_index < old_rules and state != "add":
            path = _patch_path(env, "rules") + "/" + str(new_index)
            # LD Patch requires value, so passing in dictionary
            patches.append(dict(op="remove", path=path))

        if new_rule_index <= old_rules and state != "add":
            # iterating over statements for range to be inclusive
            if new_rule_index <= len(feature_flag.rules) - 1:
                # API returns None for rollout and variation if not set
                if not rule.get("rollout"):
                    rule["rollout"] = None
                else:
                    # If there's a rule and no bucket_by, default to key
                    rule["rollout"]["bucket_by"] = rule["rollout"].get(
                        "bucket_by", "key"
                    )
                    # Weighted variations is internal ansible/API name, map to public
                    rule["rollout"]["variations"] = rule["rollout"].pop(
                        "weighted_variations"
                    )

                if rule.get("variation") is None:
                    rule["variation"] = None
                for clause in rule["clauses"]:
                    if clause.get("negate") is None:
                        clause["negate"] = False

                flag = feature_flag.rules[new_rule_index].to_dict()
                # Deleting in place is not optimal but whole dict is being iterated over before being used.
                if flag.get("clauses"):
                    for clause in flag["clauses"]:
                        del clause["id"]

                if list(
                    diff(rule, flag, ignore=set(["id", "rule_state", "track_events"]))
                ):
                    clauses_list.append(
                        list(
                            diff(
                                rule,
                                flag,
                                ignore=set(["id", "rule_state", "track_events"]),
                            )
                        )
                    )
                    path = _patch_path(env, "rules")
                    try:
                        if rule["variation"] is not None:
                            patches.append(
                                _patch_op(
                                    "replace",
                                    path + "/%d/variation" % new_rule_index,
                                    rule["variation"],
                                )
                            )
                    except KeyError:
                        pass

                    if rule["rollout"]:
                        if flag.get("variation") is not None:
                            patches.append(
                                dict(
                                    op="remove",
                                    path=path + "/%d/variation" % new_rule_index,
                                )
                            )
                            op = "add"
                        else:
                            op = "replace"
                        patches.append(
                            _patch_op(
                                op,
                                path + "/%d/rollout" % new_rule_index,
                                _build_rules(rule["rollout"]),
                            )
                        )

                    if rule["clauses"] is not None and list(
                        diff(
                            rule["clauses"],
                            flag["clauses"],
                            ignore=set(["id"]),
                        )
                    ):
                        for clause_idx, clause in enumerate(rule["clauses"]):
                            patches.append(
                                _patch_op(
                                    "replace",
                                    path
                                    + "/%d/clauses/%d/op"
                                    % (new_rule_index, clause_idx),
                                    clause["op"],
                                )
                            )
                            try:
                                patches.append(
                                    _patch_op(
                                        "replace",
                                        path
                                        + "/%d/clauses/%d/negate"
                                        % (new_rule_index, clause_idx),
                                        clause["negate"],
                                    )
                                )
                            except KeyError:
                                # pass
                                patches.append(
                                    _patch_op(
                                        "replace",
                                        path
                                        + "/%d/clauses/%d/negate"
                                        % (new_rule_index, clause_idx),
                                        False,
                                    )
                                )
                            patches.append(
                                _patch_op(
                                    "replace",
                                    path
                                    + "/%d/clauses/%d/values"
                                    % (new_rule_index, clause_idx),
                                    clause["values"],
                                )
                            )
                            patches.append(
                                _patch_op(
                                    "replace",
                                    path
                                    + "/%d/clauses/%d/attribute"
                                    % (new_rule_index, clause_idx),
                                    clause["attribute"],
                                )
                            )
                if new_rules_copy:
                    new_rules_copy.pop(0)
                flag_index += 1

    result = []
    for idx, rule_change in enumerate(new_rules_copy):
        rule = _build_rules(rule_change)
        new_flag_index = flag_index + idx
        rule_change["state"] = rule_change.get("state", "present")
        if idx > old_rules:
            path = _patch_path(env, "rules") + "/" + str(idx)
            patches.append(_patch_op("add", path, rule))
        # Non-idempotent operation - add
        elif rule_change["state"] == "add":
            pos = old_rules + idx
            path = _patch_path(env, "rules") + "/" + str(pos)
            patches.append(_patch_op("add", path, rule))
        else:
            state = rule_change["state"]
            del rule_change["state"]

            # Needed because nested defaults are not applying
            for clause in rule_change["clauses"]:
                clause["negate"] = clause.get("negate", False)
            if idx < old_rules:
                result = list(
                    diff(
                        rule_change,
                        feature_flag.rules[idx].to_dict(),
                        ignore=set(["id"]),
                    )
                )
                if result:
                    path = _patch_path(env, "rules") + "/" + str(new_flag_index)
                    patches.append(_patch_op("replace", path, rule))
                elif not result and state == "absent":
                    path = _patch_path(env, "rules") + "/" + str(new_flag_index)
                    patches.append(_patch_op("remove", path, rule))
            else:
                # If a previous rule exists increment index to add new rule
                if len(feature_flag.rules) > 0 and old_rules == 0:
                    old_rules = 1
                pos = old_rules + idx
                path = _patch_path(env, "rules") + "/" + str(pos)
                patches.append(_patch_op("add", path, rule))
    return patches, clauses_list


def _build_rules(rule):
    temp_rule = copy.deepcopy(rule)
    rollout_rule = temp_rule.get("rollout") or temp_rule.get("weighted_variations")
    if rollout_rule is not None:
        if temp_rule.get("rollout"):
            temp_cont = temp_rule["rollout"]
            del temp_rule["rollout"]

        elif temp_rule.get("weighted_variations"):
            temp_cont = {}
            temp_cont["rollout"] = temp_rule.get("weighted_variations")

        bucket_by = temp_cont.get("bucket_by", "key")

        temp_rule["rollout"] = {"bucketBy": bucket_by, "variations": []}
        try:
            for weighted_var in temp_cont["weighted_variations"]:
                temp_rule["rollout"]["variations"].append(
                    {
                        "variation": weighted_var["variation"],
                        "weight": weighted_var["weight"],
                    }
                )
        except KeyError:
            pass

        if temp_rule.get("weighted_variations"):
            for weight_var in temp_rule["weighted_variations"]:
                temp_rule["rollout"]["variations"].append(weight_var)

            del temp_rule["weighted_variations"]

    try:
        if temp_rule["variation"] is None:
            del temp_rule["variation"]
    except KeyError:
        pass
    # Not sure if needed
    try:
        if temp_rule["rollout"] is None:
            del temp_rule["rollout"]
    except KeyError:
        pass

    if rule.get("weighted_variations"):
        return temp_rule["rollout"]
    else:
        return temp_rule


def _check_prereqs(prereqs, feature_flag):
    if prereqs is not None:
        for idx, target in enumerate(prereqs):
            if idx > len(feature_flag.prerequisites) - 1:
                prereq_result = ["break"]
                break
            prereq_result = diff(target, feature_flag.prerequisites[idx].to_dict())

        if not list(prereq_result):
            del prereqs
    else:
        del prereqs


def _fetch_feature_flag(module, api_instance):
    try:
        # Get an environment given a project and key.
        feature_flag = api_instance.get_feature_flag(
            module.params["project_key"],
            module.params["flag_key"],
            env=[module.params["environment_key"]],
        )
        return feature_flag.environments[module.params["environment_key"]]
    except ApiException as e:
        if e.status == 404:
            raise AnsibleError(
                "Flag: %s does not exist in Project: %s"
                % (module.params["flag_key"], module.params["project_key"])
            )
        fail_exit(module, e)


if __name__ == "__main__":
    main()
