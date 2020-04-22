def ld_env_arg_spec():
    return dict(
        environment_key=dict(type="str", required=True, aliases=["key"]),
        color=dict(type="str"),
        name=dict(type="str"),
        default_ttl=dict(type="int"),
        tags=dict(type="list", elements="str"),
        confirm_changes=dict(type="bool"),
        require_comments=dict(type="bool"),
        default_track_events=dict(type="bool"),
    )


def env_ld_builder(environments):
    patches = []
    for env in environments:
        env_mapped = dict(
            (launchdarkly_api.Environment.attribute_map[k], v)
            for k, v in env.items()
            if v is not None
        )

        patches.append(launchdarkly_api.EnvironmentPost(**env))
    return patches
