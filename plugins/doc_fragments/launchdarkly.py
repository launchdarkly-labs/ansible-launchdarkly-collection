class ModuleDocFragment(object):
    # Launchdarkly common documentation
    DOCUMENTATION = r"""
    options:
        api_key:
            description:
                - LaunchDarkly API access token. May be set as C(LAUNCHDARKLY_ACCESS_TOKEN) environment variable.
            type: str
            required: yes
    """
