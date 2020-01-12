from __future__ import absolute_import, division, print_function

__metaclass__ = type

import launchdarkly_api

def configure_instance(api_key):
    configuration = launchdarkly_api.Configuration()
    configuration.api_key["Authorization"] = api_key
    return configuration


def _patch_path(module, op):
    return "/environments/" + module.params["environment_key"] + "/" + op


def _build_comment(module):
    if module.params.get("comment") or module.params["comment"]:
        comment = module.params["comment"]
    else:
        comment = "Ansible generated operation."
    return comment


def _patch_op(op, path, value):
    return launchdarkly_api.PatchOperation(op=op, path=path, value=value)

def parse_env_param(module, param_name, key=None):
    if key is None:
        key = launchdarkly_api.Environment.attribute_map[param_name]
    path = "/" + key
    return launchdarkly_api.PatchOperation(
        path=path, op="replace", value=module[param_name]
    )


def parse_user_param(module, param_name, key=None):
    if key is None:
        key = launchdarkly_api.UserSegment.attribute_map[param_name]
    path = "/" + key
    patch = dict(path=path, op="replace", value=module[param_name])
    return launchdarkly_api.PatchOperation(**patch)


def reset_rate(reset_time):
    current = time.time() * 1000.0
    return int((float(reset_time) - current + 1000.0) / 1000.0)
