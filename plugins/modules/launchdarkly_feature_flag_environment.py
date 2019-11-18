#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "0.1.0",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r'''
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
            - LaunchDarkly API Key. May be set as LAUNCHDARKLY_ACCESS_TOKEN environment variable.
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
    rules:
        description:
            - Target users based on user attributes
        type: list
    fallthrough:
        description: |
            - Nested dictionary describing the default variation to serve if no 'prerequisites',
            - 'targets', or 'rules' apply.
'''

EXAMPLES = r'''
---
# Create a new flag
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
'''

RETURN = r'''
---
feature_flag_environment:
    description: Dictionary containing a L(Feature Flag Config, https://github.com/launchdarkly/api-client-python/blob/2.0.21/docs/FeatureFlagConfig.md)
    type: dict
    returned: on success
'''

import inspect
import traceback
from operator import itemgetter
from itertools import groupby


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
from ansible.module_utils.basic import AnsibleModule, missing_required_lib, env_fallback
from ansible.module_utils._text import to_native
from ansible.module_utils.common._json_compat import json
from ansible.module_utils.six import PY2, iteritems, string_types


# from rule import rule_argument_spec
# from base import configure_instance, _patch_path, _build_comment, _patch_op

from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import (
    configure_instance,
    _patch_path,
    _patch_op,
    _build_comment,
)
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.rule import (
    rule_argument_spec,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                type="str",
                default="present",
                choices=["absent", "present", "enabled", "disabled"],
            ),
            api_key=dict(
                required=True,
                type="str",
                no_log=True,
                fallback=(env_fallback, ["LAUNCHDARKLY_ACCESS_TOKEN"]),
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
                        choices=["add", "remove", "replace"],
                    ),
                ),
            ),
            fallthrough=dict(
                type="dict",
                options=dict(
                    variation=dict(type="int"),
                    rollout=dict(
                        type="list",
                        elements="dict",
                        options=dict(
                            variation=dict(type="int"), weight=dict(type="int")
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
    if module.params["prerequisites"] is not None:
        for idx, target in enumerate(module.params["prerequisites"]):
            if idx > len(feature_flag.prerequisites) - 1:
                prereq_result = ["break"]
                break
            prereq_result = diff(target, feature_flag.prerequisites[idx].to_dict())

        if len(list(prereq_result)) == 0:
            del module.params["prerequisites"]

    # Loop over targets comparing
    if module.params["targets"] is not None:
        # Check if targets already exist in variation
        target_list = []
        for item in feature_flag.targets:
            target_list.append(item.to_dict())
        feature_flag_targets = target_list
        for item in feature_flag_targets:
            item.update({"state": "existing"})

        for item in module.params["targets"]:
            item.update({"state": "new"})

        all_targets = feature_flag_targets + module.params["targets"]
        end_targets = []
        for variation, items in groupby(all_targets, key=itemgetter("variation")):
            old_targets = []
            new_targets = []
            loop_items = list(items)
            if len(loop_items) == 2:
                for i in loop_items:
                    if i["state"] == "existing":
                        old_targets = i["values"]
                    else:
                        new_targets = i["values"]

                if set(new_targets).issubset(set(old_targets)):
                    continue
                else:
                    end_targets.append(
                        {
                            "variation": i["variation"],
                            "new_targets": list(
                                set(new_targets).difference(old_targets)
                            ),
                            "old_targets": len(old_targets),
                        }
                    )

            else:
                for i in loop_items:
                    if i["state"] == "existing":
                        continue
                    else:
                        end_targets.append(
                            {"variation": i["variation"], "new_targets": i["values"]}
                        )

        new_variations = end_targets

        for i, item in enumerate(end_targets):
            for idx, orig_target in enumerate(feature_flag_targets):
                if item["variation"] == orig_target["variation"]:
                    for place, val in enumerate(item["new_targets"]):
                        new_entry = item["old_targets"] + place
                        path = (
                            _patch_path(module, "targets")
                            + "/"
                            + str(idx)
                            + "/values/"
                            + str(new_entry)
                        )
                        patches.append(_patch_op("add", path, val))
                    del new_variations[i]

        for item in new_variations:
            path = _patch_path(module, "targets") + "/0"
            patches.append(
                _patch_op(
                    "add",
                    path,
                    {"variation": item["variation"], "values": item["new_targets"]},
                )
            )

        del module.params["targets"]

    # Loop over rules comparing
    if module.params["rules"] is not None:
        oldRules = len(feature_flag.rules) - 1
        newRules = len(module.params["rules"])
        newIndex = newRules - 1
        newRulesCopy = module.params["rules"]
        for ruleIndex, newRule in enumerate(module.params["rules"]):
            if newIndex < oldRules and newRule["state"] != "add":
                # iterating over statements for range to be inclusive
                for i in range(newRules, len(feature_flag.rules)):
                    path = _patch_path(module, "rules") + "/" + str(newRules)
                    patches.append(
                        launchdarkly_api.PatchOperation(
                            op="remove", path=path, value="needed_for_call"
                        )
                    )

                for i in range(newIndex):
                    if diff(module.params["rules"][i], feature_flag.rules[i].to_dict()):
                        path = _patch_path(module, "rules")
                        if module.params["rules"][i]["variation"] is not None:
                            patches.append(
                                _patch_op(
                                    "replace",
                                    path + "/%d/variation" % i,
                                    module.params["rules"][i]["variation"],
                                )
                            )
                        if module.params["rules"][i]["rollout"] is not None:
                            patches.append(
                                _patch_op(
                                    "replace",
                                    path + "/%d/rollout" % i,
                                    module.params["rules"][i]["rollout"],
                                )
                            )
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
                                        path + "/%d/clauses/%d/attribute" % (i, idx),
                                        clause["attribute"],
                                    )
                                )

                        del newRulesCopy[i]

        result = []
        for idx, ruleChange in enumerate(newRulesCopy):
            rule = _build_rules(ruleChange)
            if idx > oldRules:
                path = _patch_path(module, "rules") + "/" + str(idx)
                patches.append(_patch_op("add", path, rule))
            # Non-idempotent operation
            elif ruleChange["state"] == "add":
                pos = oldRules + idx
                path = _patch_path(module, "rules") + "/" + str(pos)
                patches.append(_patch_op("add", path, rule))
            else:
                state = ruleChange["state"]
                del ruleChange["state"]
                result = list(
                    diff(
                        ruleChange,
                        feature_flag.rules[idx].to_dict(),
                        ignore=set(["id"]),
                    )
                )
                if len(result) > 0:
                    path = _patch_path(module, "rules") + "/" + str(idx)
                    patches.append(_patch_op("replace", path, rule))
                elif len(result) == 0 and state == "absent":
                    path = _patch_path(module, "rules") + "/" + str(idx)
                    patches.append(_patch_op("remove", path, rule))
        del module.params["rules"]

    # Compare fallthrough
    fallthrough = diff(
        module.params["fallthrough"],
        feature_flag.fallthrough.to_dict(),
        ignore=set(["id"]),
    )
    if len(list(fallthrough)) == 0:
        del module.params["fallthrough"]
    else:
        fallthrough = _build_rules(module.params["fallthrough"])
        op = "replace"
        path = _patch_path(module, "fallthrough")
        patches.append(_patch_op(op, path, fallthrough))
        # Delete key so it's not pass through to next loop
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

    if len(patches) > 0:
        comment = _build_comment(module)
        comments = dict(comment=comment, patch=patches)
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

    module.exit_json(changed=False, msg="flag environment unchanged", feature_flag_environment=feature_flag)


def _build_rules(rule):
    temp_rule = rule
    if temp_rule.get("rollout"):
        temp_cont = temp_rule["rollout"]
        del temp_rule["rollout"]
        temp_rule["rollout"] = {"variations": temp_cont}

    if temp_rule["variation"] is None or temp_rule.get("variation") is None:
        del temp_rule["variation"]
    return temp_rule


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
        else:
            err = json.loads(str(e.body))
            raise AnsibleError("Error: %s" % to_native(err.body))


if __name__ == "__main__":
    main()
