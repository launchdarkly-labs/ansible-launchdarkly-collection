import traceback

try:
    import launchdarkly_api
    from launchdarkly_api.rest import ApiException

    # from dictdiffer import diff

    HAS_LD = True
except ImportError:
    LD_IMP_ERR = traceback.format_exc()
    HAS_LD = False


def configure_defaults(fflag_body, flag):
    if flag["defaults"] and flag["defaults"] is not None:
        fflag_body["defaults"] = dict(
            (launchdarkly_api.Defaults.attribute_map[k], v)
            for k, v in flag["defaults"].items()
            if v is not None
        )
    return fflag_body

def configure_clientside_avail(fflag_body, flag):
    if (
    flag["client_side_availability"]
    and flag["client_side_availability"] is not None
    ):
        fflag_body["client_side_availability"] = dict(
            (launchdarkly_api.ClientSideAvailability.attribute_map[k], v)
            for k, v in flag["client_side_availability"].items()
            if v is not None
        )

    return fflag_body
