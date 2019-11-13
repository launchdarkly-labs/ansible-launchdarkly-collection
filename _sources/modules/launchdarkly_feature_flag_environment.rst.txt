:source: 


.. _launchdarkly_feature_flag_environment_:


launchdarkly_feature_flag_environment -- Create Environment specific flag targeting
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 0.1.0

.. contents::
   :local:
   :depth: 1


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
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>LaunchDarkly API Key. May be set as LAUNCHDARKLY_ACCESS_TOKEN environment variable.</div>
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
                                            <div>A unique key that will be used to reference the environment.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>fallthrough</b>
                    <div style="font-size: small">
                        <span style="color: purple">-</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>-</div>
                                            <div></div>
                                            <div>N</div>
                                            <div>e</div>
                                            <div>s</div>
                                            <div>t</div>
                                            <div>e</div>
                                            <div>d</div>
                                            <div></div>
                                            <div>d</div>
                                            <div>i</div>
                                            <div>c</div>
                                            <div>t</div>
                                            <div>i</div>
                                            <div>o</div>
                                            <div>n</div>
                                            <div>a</div>
                                            <div>r</div>
                                            <div>y</div>
                                            <div></div>
                                            <div>d</div>
                                            <div>e</div>
                                            <div>s</div>
                                            <div>c</div>
                                            <div>r</div>
                                            <div>i</div>
                                            <div>b</div>
                                            <div>i</div>
                                            <div>n</div>
                                            <div>g</div>
                                            <div></div>
                                            <div>t</div>
                                            <div>h</div>
                                            <div>e</div>
                                            <div></div>
                                            <div>d</div>
                                            <div>e</div>
                                            <div>f</div>
                                            <div>a</div>
                                            <div>u</div>
                                            <div>l</div>
                                            <div>t</div>
                                            <div></div>
                                            <div>v</div>
                                            <div>a</div>
                                            <div>r</div>
                                            <div>i</div>
                                            <div>a</div>
                                            <div>t</div>
                                            <div>i</div>
                                            <div>o</div>
                                            <div>n</div>
                                            <div></div>
                                            <div>t</div>
                                            <div>o</div>
                                            <div></div>
                                            <div>s</div>
                                            <div>e</div>
                                            <div>r</div>
                                            <div>v</div>
                                            <div>e</div>
                                            <div></div>
                                            <div>i</div>
                                            <div>f</div>
                                            <div></div>
                                            <div>n</div>
                                            <div>o</div>
                                            <div></div>
                                            <div>'</div>
                                            <div>p</div>
                                            <div>r</div>
                                            <div>e</div>
                                            <div>r</div>
                                            <div>e</div>
                                            <div>q</div>
                                            <div>u</div>
                                            <div>i</div>
                                            <div>s</div>
                                            <div>i</div>
                                            <div>t</div>
                                            <div>e</div>
                                            <div>s</div>
                                            <div>'</div>
                                            <div>,</div>
                                            <div></div>
                                            <div>-</div>
                                            <div></div>
                                            <div>'</div>
                                            <div>t</div>
                                            <div>a</div>
                                            <div>r</div>
                                            <div>g</div>
                                            <div>e</div>
                                            <div>t</div>
                                            <div>s</div>
                                            <div>'</div>
                                            <div>,</div>
                                            <div></div>
                                            <div>o</div>
                                            <div>r</div>
                                            <div></div>
                                            <div>'</div>
                                            <div>r</div>
                                            <div>u</div>
                                            <div>l</div>
                                            <div>e</div>
                                            <div>s</div>
                                            <div>'</div>
                                            <div></div>
                                            <div>a</div>
                                            <div>p</div>
                                            <div>p</div>
                                            <div>l</div>
                                            <div>y</div>
                                            <div>.</div>
                                            <div></div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>off_variation</b>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>Variation served if flag targeting is turned off.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>project_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">-</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">"default"</div>
                                    </td>
                                <td>
                                            <div>Project key will group flags together</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>rules</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>Target users based on user attributes</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>state</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
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
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
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
                op: contains
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
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>on success</td>
                <td>
                                            <div>Dictionary containing a <a href='https://github.com/launchdarkly/api-client-python/blob/2.0.21/docs/FeatureFlagConfig.md'>Feature Flag Config</a></div>
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
