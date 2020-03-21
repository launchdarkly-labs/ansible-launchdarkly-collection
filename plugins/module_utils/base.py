import launchdarkly_api
import time
from ansible.module_utils._text import to_native
from ansible.errors import AnsibleError, AnsibleAuthenticationFailure
from ansible.module_utils.common._json_compat import json
from ansible.module_utils.basic import env_fallback

VERSION = "0.2.12"


def configure_instance(api_key):
    configuration = launchdarkly_api.Configuration()
    configuration.api_key["Authorization"] = api_key
    configuration.user_agent = "launchdarkly-ansible-collection/%s" % VERSION
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


def fail_exit(module, e):
    if e.reason == "Unauthorized":
        raise AnsibleAuthenticationFailure(to_native(e.reason))
    elif e.body is not None:
        err = json.loads(str(e.body))
        raise AnsibleError(err["message"])
    else:
        return module.exit_json(failed=True, msg=to_native(e.reason))


def ld_common_argument_spec():
    return dict(
        api_key=dict(
            required=True,
            type="str",
            no_log=True,
            fallback=(env_fallback, ["LAUNCHDARKLY_ACCESS_TOKEN"]),
        ),
        conftest=dict(
            type="dict",
            apply_defaults=True,
            options=dict(
                dir=dict(type="str", default="policy"),
                namespace=dict(type="str", default="launchdarkly"),
                enabled=dict(type="bool", default=False),
            ),
        ),
    )


def rego_test(module, validate):
    try:
        from policykit import Conftest
    except ImportError:
        module.fail_json(
            msg=missing_required_lib("policykit"), exception=traceback.format_exc()
        )
    try:
        run = Conftest(module.params["conftest"]["dir"]).test(
            namespace=module.params["conftest"]["namespace"], json_input=validate
        )
    except Exception as e:
        raise AnsibleError(e)

    return run


def validate_params(module):
    keys = ["api_key", "state"]

    check_params = dict((k, module.params[k]) for k in module.params if k not in keys)
    result = rego_test(module, check_params)

    if result.results[0].failures:
        module.exit_json(failed=True, validation=result.results[0].failures)
