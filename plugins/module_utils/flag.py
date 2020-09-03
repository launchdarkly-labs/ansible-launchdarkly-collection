import traceback

try:
    import launchdarkly_api
    from launchdarkly_api.rest import ApiException

    # from dictdiffer import diff

    HAS_LD = True
except ImportError:
    LD_IMP_ERR = traceback.format_exc()
    HAS_LD = False


def defaults_configure(fflag_body, flag):
    if flag["defaults"] and flag["defaults"] is not None:
        fflag_body["defaults"] = dict(
            (launchdarkly_api.Defaults.attribute_map[k], v)
            for k, v in flag["defaults"].items()
            if v is not None
        )
    return fflag_body
