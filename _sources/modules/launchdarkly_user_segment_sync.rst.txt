:source: 


.. _launchdarkly_user_segment_sync_:


launchdarkly_user_segment_sync -- Sync LaunchDarkly User Segments across Environments
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 0.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Sync LaunchDarkly User Segments across Environments




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
                    <b>excludedActions</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>updateTargets&#39;</li>
                                                                                                                                                                                                <li>updateRules</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                            <div>Manage a list of excluded actions for copying.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>includedActions</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>updateTargets</li>
                                                                                                                                                                                                <li>updateRules</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                            <div>Manage a list of included actions for copying.</div>
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
                                <tr>
                                                                <td colspan="1">
                    <b>user_segment_key</b>
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
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
    # Sync a LaunchDarkly User Segment to multiple environments
    - launchdarkly_user_segment_sync:
        environment_key: test-environment-1
        environment_targets:
            - dev
            - staging
            - production
        name: "Test Segment"
        includedActions:
          - updateOn
          - updateRules





Status
------




- This  is not guaranteed to have a backwards compatible interface. *[preview]*


- This  is :ref:`maintained by the Ansible Community <modules_support>`. *[community]*






.. hint::
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/plugins//?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.


.. hint::
    Configuration entries for each entry type have a low to high priority order. For example, a variable that is lower in the list will override a variable that is higher up.
