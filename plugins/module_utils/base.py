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
