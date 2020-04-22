:source: 


.. _launchdarkly_project_info_:


launchdarkly_project_info -- Return a Project or List of Projects
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 0.2.11

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Return a dictionary of a single LaunchDarkly Project or List of dictionaries containing LaunchDarkly Projects




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
                    <tr>
                                                                <td colspan="1">
                    <b>api_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>LaunchDarkly API Key. May be set as <code>LAUNCHDARKLY_ACCESS_TOKEN</code> environment variable.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>environment_tags</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>list of tags to filter environments within the project. Only environments that contain one of the tags will be returned.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>project_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>Project key is used to return a single project matching that key.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>tags</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>list of tags to filter projects. Only projects that contain one of the tags will be returned</div>
                                                        </td>
            </tr>
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
    # Get project based on its key.
    - launchdarkly_project_info:
        api_key: api-12345
        project_key: example-project

    # Get list of projects that are tagged "dev"
    - launchdarkly_project_info:
        api_key: api-12345
        tags:
          - dev

    # Get list of projects that are tagged "dev" and only return environments tagged "prod"
    - launchdarkly_project_info:
        api_key: api-12345
        tags:
          - dev
        environment_tags:
          - prod

    # Get list of all projects only return environments tagged "prod"
    - launchdarkly_project_info:
        api_key: api-12345
        environment_tags:
          - prod




Return Values
-------------
Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this :

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
                    <tr>
                                <td colspan="1">
                    <b>project</b>
                    <div style="font-size: small">
                      <span style="color: purple">dict or list</span>
                                          </div>
                                    </td>
                <td>on success</td>
                <td>
                                            <div>Dictionary or List of Dictionaries containing a <a href='https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/Project.md'>Project</a></div>
                                        <br/>
                                    </td>
            </tr>
                        </table>
    <br/><br/>


Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is :ref:`maintained by the Ansible Community <modules_support>`. *[community]*






.. hint::
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/plugins//?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.


.. hint::
    Configuration entries for each entry type have a low to high priority order. For example, a variable that is lower in the list will override a variable that is higher up.
