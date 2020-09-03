def defaults_configure(fflag_body, flag):
    if flag["defaults"] and flag["defaults"] is not None:
        fflag_body["defaults"] = dict(
            (launchdarkly_api.Defaults.attribute_map[k], v)
            for k, v in flag["defaults"].items()
            if v is not None
        )
    return fflag_body
