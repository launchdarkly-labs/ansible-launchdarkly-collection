:source: 


.. _launchdarkly_feature_flag_sync_:


launchdarkly_feature_flag_sync -- Sync LaunchDarkly Feature Flags across Environments
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 0.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Sync LaunchDarkly Feature Flags across Environments




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
                    <b>environment_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>A unique key that will be used to determine source environment.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>environment_targets</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>A list of environments that flag settings will be copied to.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>excluded_actions</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>updateOn</li>
                                                                                                                                                                                                <li>updatePrerequisites</li>
                                                                                                                                                                                                <li>updateTargets</li>
                                                                                                                                                                                                <li>updateRules</li>
                                                                                                                                                                                                <li>updateFallthrough</li>
                                                                                                                                                                                                <li>updateOffVariation</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                            <div>Manage a list of excluded actions for copying.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>flag_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>A unique key that will be used to reference the user segment in this environment.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>included_actions</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>updateOn</li>
                                                                                                                                                                                                <li>updatePrerequisites</li>
                                                                                                                                                                                                <li>updateTargets</li>
                                                                                                                                                                                                <li>updateRules</li>
                                                                                                                                                                                                <li>updateFallthrough</li>
                                                                                                                                                                                                <li>updateOffVariation</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                            <div>Manage a list of included actions for copying. If not specified all actions are included.</div>
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
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">"default"</div>
                                    </td>
                                <td>
                                            <div>Project key to look for flag</div>
                                                        </td>
            </tr>
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
    # Sync a LaunchDarkly Feature Flag Configuration across environments
    - launchdarkly_feature_flag_sync:
        environment_key: test-environment-1
        environment_targets:
            - dev
            - staging
            - production
        flag_key: test_flag_1
        project_key: test_project
        included_actions:
          - updateOn
          - updateRules




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
                    <b>feature_flag</b>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>on success</td>
                <td>
                                            <div>Dictionary containing a <a href='https://github.com/launchdarkly/api-client-python/blob/2.0.30/docs/FeatureFlag.md'>Feature Flag</a></div>
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
