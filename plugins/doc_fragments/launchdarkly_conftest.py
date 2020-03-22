class ModuleDocFragment(object):
    # Launchdarkly common documentation
    DOCUMENTATION = r"""
    options:
        conftest:
            description:
                - Run a conftest policy when creating resource.
            type: str
            required: no
            suboptions:
                enabled:
                    description:
                        - Run Policy
                    type: bool
                    required: no
                dir:
                    description:
                        - Directory to look for policy
                    type: str
                    required: no
                namespace:
                    description:
                        - Conftest namespace to apply
                    type: str
                    required: no
                    default: launchdarkly
    """
