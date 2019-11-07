
:source: 


.. _launchdarkly_feature_flag_environment_:


launchdarkly_feature_flag_environment - Create Environment specific flag targeting
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.9

.. contents::
   :local:
   :depth: 2


Synopsis
--------
- Manage LaunchDarkly manage feature flags and account settings.




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
                    <br/><div style="font-size: small; color: red">str</div>                    <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>LaunchDarkly API Key</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>environment_key</b>
                    <br/><div style="font-size: small; color: red">str</div>                    <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>A unique key that will be used to reference the environment.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>fallthrough</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>Nested dictionary describing the default variation to serve if no 'prerequisites', 'targets', or 'rules' apply.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>off_variation</b>
                    <br/><div style="font-size: small; color: red">int</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>Variation served if flag targeting is turned off.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>project_key</b>
                                                                            </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">default</div>
                                    </td>
                                <td>
                                                                        <div>Project key will group flags together</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>rules</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>Target users based on user attributes</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>state</b>
                    <br/><div style="font-size: small; color: red">str</div>                                                        </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li>absent</li>
                                                                                                                                                                                                <li>enabled</li>
                                                                                                                                                                                                <li>disabled</li>
                                                                                                                                                                                                <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                                                        <div>Indicate desired state of the resource</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>targets</b>
                    <br/><div style="font-size: small; color: red">list</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>Assign users to a specific variation</div>
                                                                                </td>
            </tr>
                        </table>
    <br/>



Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Create a new flag
    - launchdarkly_feature_flag_environment:
        state: present
        flag_key: example_flag
        environment_key: default
        off_variation: 1
        targets:
            - variation: 1
              values:
                - test@example.com
                - test2@example.com

        comment: Updating default env values

    - launchdarkly_feature_flag_environment:
        state: enabled
        flag_key: example_2
        environment_key: env_2
        fallthrough:
          variation: 1
        rules:
        - variation: 1
            clauses:
            - attribute: test-attribute
                op: "contains"
                values:
                - 2
                - 3
                negate: true
        prerequisites:
          - variation: 0
            key: example_flag




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
                    <b>feature_flag_environment</b>
                    <br/><div style="font-size: small; color: red">dict</div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Dictionary containing environment specific configuration</div>
                                        <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{'test': 'test'}</div>
                                    </td>
            </tr>
                        </table>
    <br/><br/>


Status
------



This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.





.. hint::
    If you notice any issues in this documentation you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/plugins//>`_ to improve it.
