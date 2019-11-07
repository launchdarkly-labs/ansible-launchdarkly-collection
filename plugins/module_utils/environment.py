def ld_env_arg_spec():
    return dict(
        environment_key=dict(type="str", required=True, aliases=["key"]),
        color=dict(type="str"),
        name=dict(type="str"),
        default_ttl=dict(type="int"),
    )


def env_ld_builder(environments):
    patches = []
    for env in environments:
        patches.append(launchdarkly_api.EnvironmentPost(**env))
    return patches
