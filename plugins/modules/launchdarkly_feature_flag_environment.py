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
short_description: Create Environment specific flag targeting
description:
     - Manage LaunchDarkly manage feature flags and account settings.
version_added: "0.1.0"
options:
    state:
        description:
            - Indicate desired state of the resource
        choices: [ absent, enabled, disabled, present ]
        default: present
        type: str
    api_key:
        description:
            - LaunchDarkly API Key. May be set as C(LAUNCHDARKLY_ACCESS_TOKEN) environment variable.
        type: str
        required: yes
    project_key:
        description:
            - Project key will group flags together
        default: 'default'
    environment_key:
        description:
            - A unique key that will be used to reference the environment.
        required: yes
        type: str
    off_variation:
        description:
            - Variation served if flag targeting is turned off.
        type: int
    targets:
        description:
            - Assign users to a specific variation
        type: list
        suboptions:
            variation:
                description:
                    - index of variation to serve default. Exclusive of rollout.
                type: int
            values:
                description:
                    - individual targets to add to variation
            state:
                choices: [ absent, add, remove, replace ]
                default: replace
    rules:
        description:
            - Target users based on user attributes
        type: list
    fallthrough:
        description:
            - Nested dictionary describing the default variation to serve if no C(prerequisites),
            - C(targets) or C(rules) apply.
        suboptions:
            variation:
                description:
                    - index of variation to serve default. Exclusive of rollout.
                type: int
            rollout:
                description:
                    - rollout value
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
    description: Dictionary containing a L(Feature Flag Config, https://github.com/launchdarkly/api-client-python/blob/2.0.24/docs/FeatureFlagConfig.md)
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
from ansible.module_utils.six import PY2

from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    _patch_path,
    _patch_op,
    _build_comment,
    fail_exit,
    ld_common_argument_spec,
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


def _toggle_flag(module, patches, feature_flag):
    if module.params["state"] == "enabled":
        value = True
    elif module.params["state"] == "disabled":
        value = False
    else:
        value = feature_flag.on

    if feature_flag.on != value:
        path = _patch_path(module, "on")
        patches.append(
            launchdarkly_api.PatchOperation(path=path, op="replace", value=value)
        )

    return patches


def _parse_flag_param(module, key, op="replace"):
    path = _patch_path(module, launchdarkly_api.FeatureFlagConfig.attribute_map[key])

    return launchdarkly_api.PatchOperation(path=path, op=op, value=module.params[key])


def _configure_feature_flag_env(module, api_instance, feature_flag=None):
    patches = []

    _toggle_flag(module, patches, feature_flag)

    if feature_flag.off_variation == module.params["off_variation"]:
        del module.params["off_variation"]

    # Loop over prerequisites comparing
    _check_prereqs(module, feature_flag)
    # Loop over targets comparing
    if module.params["targets"] is not None:
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
        for target in module.params["targets"]:
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
                        val_index = flag_var_index[target["variation"]]["index"]
                        new_targets_idx = len(
                            flag_var_index[target["variation"]]["targets"]
                        )
                        for val_idx, val in enumerate(new_targets):
                            new_idx = str(new_targets_idx + val_idx)
                            path = (
                                _patch_path(module, "targets")
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
                target_index = str(flag_var_index[target["variation"]]["index"])

                path = _patch_path(module, "targets") + "/" + target_index
                patches.append(dict(op="remove", path=path))
                continue

            path = _patch_path(module, "targets") + "/" + target_index
            patches.append(
                _patch_op(
                    target["state"],
                    path,
                    {"variation": target["variation"], "values": list(new_targets)},
                )
            )

        del module.params["targets"]

    # Loop over rules comparing
    if module.params["rules"] is not None:
        old_rules = max(len(feature_flag.rules) - 1, 0)
        new_rules = len(module.params["rules"])
        new_index = new_rules - 1
        # Make copy for next step.
        new_rules_copy = copy.deepcopy(module.params["rules"])
        flag_index = 0
        add_guard = False
        for new_rule in module.params["rules"]:
            state = new_rule.get("rule_state", "present")
            del new_rule["rule_state"]
            if new_index <= old_rules and state != "add":
                # iterating over statements for range to be inclusive
                if not add_guard:
                    # We only want to loop over old rules once removing
                    add_guard = True
                    for i in range(new_index, old_rules):
                        path = _patch_path(module, "rules") + "/" + str(i)
                        # LD Patch requires value, so passing in dictionary
                        patches.append(dict(op="remove", path=path))
                # iterating over statements for range to be inclusive
                for i in range(new_index):
                    if i <= len(feature_flag.rules):
                        if list(
                            diff(
                                module.params["rules"][i],
                                feature_flag.rules[i].to_dict(),
                                ignore=set(["id", "rule_state"]),
                            )
                        ):
                            path = _patch_path(module, "rules")
                            if module.params["rules"][i]["variation"] is not None:
                                patches.append(
                                    _patch_op(
                                        "replace",
                                        path + "/%d/variation" % i,
                                        module.params["rules"][i]["variation"],
                                    )
                                )

                            try:
                                if module.params["rules"][i]["rollout"] is not None:
                                    patches.append(
                                        _patch_op(
                                            "replace",
                                            path + "/%d/rollout" % i,
                                            module.params["rules"][i]["rollout"],
                                        )
                                    )
                            except KeyError:
                                pass

                            if module.params["rules"][i]["clauses"] is not None:
                                for idx, clause in enumerate(
                                    module.params["rules"][i]["clauses"]
                                ):
                                    patches.append(
                                        _patch_op(
                                            "replace",
                                            path + "/%d/clauses/%d/op" % (i, idx),
                                            clause["op"],
                                        )
                                    )
                                    patches.append(
                                        _patch_op(
                                            "replace",
                                            path + "/%d/clauses/%d/negate" % (i, idx),
                                            clause["negate"],
                                        )
                                    )
                                    patches.append(
                                        _patch_op(
                                            "replace",
                                            path + "/%d/clauses/%d/values" % (i, idx),
                                            clause["values"],
                                        )
                                    )
                                    patches.append(
                                        _patch_op(
                                            "replace",
                                            path
                                            + "/%d/clauses/%d/attribute" % (i, idx),
                                            clause["attribute"],
                                        )
                                    )
                        if new_rules_copy:
                            new_rules_copy.pop()
                        flag_index += 1

        result = []
        for idx, rule_change in enumerate(new_rules_copy):
            rule = _build_rules(rule_change)
            new_flag_index = flag_index + idx
            rule_change["state"] = rule_change.get("state", "present")
            if idx > old_rules:
                path = _patch_path(module, "rules") + "/" + str(idx)
                patches.append(_patch_op("add", path, rule))
            # Non-idempotent operation - add
            elif rule_change["state"] == "add":
                pos = old_rules + idx
                path = _patch_path(module, "rules") + "/" + str(pos)
                patches.append(_patch_op("add", path, rule))
            else:
                state = rule_change["state"]
                del rule_change["state"]

                # Needed because nested defaults are not applying
                for clause in rule_change["clauses"]:
                    clause["negate"] = clause.get("negate", False)
                if idx <= old_rules:
                    result = list(
                        diff(
                            rule_change,
                            feature_flag.rules[idx].to_dict(),
                            ignore=set(["id"]),
                        )
                    )
                    if result:
                        path = _patch_path(module, "rules") + "/" + str(new_flag_index)
                        patches.append(_patch_op("replace", path, rule))
                    elif not result and state == "absent":
                        path = _patch_path(module, "rules") + "/" + str(new_flag_index)
                        patches.append(_patch_op("remove", path, rule))
                else:
                    pos = old_rules + idx
                    path = _patch_path(module, "rules") + "/" + str(pos)
                    patches.append(_patch_op("add", path, rule))
        del module.params["rules"]

    # Compare fallthrough
    fallthrough = diff(
        module.params["fallthrough"],
        feature_flag.fallthrough.to_dict(),
        ignore=set(["id"]),
    )
    if not list(fallthrough):
        del module.params["fallthrough"]
    else:
        fallthrough = _build_rules(module.params["fallthrough"])
        op = "replace"
        path = _patch_path(module, "fallthrough")
        patches.append(_patch_op(op, path, fallthrough))
        # Delete key so it's not passed through to next loop
        del module.params["fallthrough"]

    for key in module.params:
        if (
            key
            not in [
                "state",
                "api_key",
                "environment_key",
                "project_key",
                "flag_key",
                "comment",
            ]
            and module.params[key] is not None
        ):
            patches.append(_parse_flag_param(module, key))

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

        module.exit_json(
            changed=True,
            msg="flag environment successfully configured",
            feature_flag_environment=api_response.to_dict(),
        )

    module.exit_json(
        changed=False,
        msg="flag environment unchanged",
        feature_flag_environment=feature_flag.to_dict(),
    )


def _build_rules(rule):
    temp_rule = rule
    if temp_rule.get("rollout"):
        temp_cont = temp_rule["rollout"]
        del temp_rule["rollout"]
        bucket_by = temp_cont.get("bucket_by", "key")
        temp_rule["rollout"] = {"bucketBy": bucket_by, "variations": []}
        for weighted_var in temp_cont["weighted_variations"]:
            temp_rule["rollout"]["variations"].append(
                {
                    "variation": weighted_var["variation"],
                    "weight": weighted_var["weight"],
                }
            )

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

    return temp_rule


def _check_prereqs(module, feature_flag):
    if module.params["prerequisites"] is not None:
        for idx, target in enumerate(module.params["prerequisites"]):
            if idx > len(feature_flag.prerequisites) - 1:
                prereq_result = ["break"]
                break
            prereq_result = diff(target, feature_flag.prerequisites[idx].to_dict())

        if not list(prereq_result):
            del module.params["prerequisites"]


def _fetch_feature_flag(module, api_instance):
    try:
        # Get an environment given a project and key.
        feature_flag = api_instance.get_feature_flag(
            module.params["project_key"],
            module.params["flag_key"],
            env=module.params["environment_key"],
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
