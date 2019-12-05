from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError
import os
from ansible_collections.launchdarkly_labs.collection.plugins.module_utils.base import configure_instance

try:
    import launchdarkly_api
    from launchdarkly_api.rest import ApiException

    HAS_LD = True
except ImportError as e:
    HAS_LD = False

class LookupModule(LookupBase):

    def run(self, terms, api_key=None, **kwargs):
        try:
            api_key = os.environ.get('LAUNCHDARKLY_ACCESS_TOKEN', api_key)
            configuration = configure_instance(api_key)

            api_instance = launchdarkly_api.UserSegmentsApi(launchdarkly_api.ApiClient(configuration))
        except Exception as e:
            raise AnsibleError('Error starting LaunchDarkly SDK: %s' % e)

        project = terms[0]
        environment = terms[1]
        #TODO add tag support
        #tags = terms[2]
        ret = []
        project = api_instance.get_user_segments(project, environment)
        ret.append(project)
        return ret
