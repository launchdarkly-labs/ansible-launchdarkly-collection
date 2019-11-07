
:source: 


.. _launchdarkly_environment_:


launchdarkly_environment - Create Launchdarkly Project specific Environment
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.9

.. contents::
   :local:
   :depth: 2


Synopsis
--------
- Manage LaunchDarkly Project specific Environments.




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
                    <b>color</b>
                    <br/><div style="font-size: small; color: red">str</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>Color used in dashboard for the environment.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>confirm_changes</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                        <ul><b>Choices:</b>
                                                                                                                                                                <li>no</li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                                                        <div>Determines if this environment requires confirmation for flag and segment changes.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>default_track_events</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                        <ul><b>Choices:</b>
                                                                                                                                                                <li>no</li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                                                        <div>Set to `true` to send detailed event information for new flags.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>default_ttl</b>
                    <br/><div style="font-size: small; color: red">int</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>TTL is only used in our PHP SDK.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>environment_key</b>
                    <br/><div style="font-size: small; color: red">str</div>                    <br/><div style="font-size: small; color: red">required</div>                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>A unique key that will be used to reference the flag in your code.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>name</b>
                    <br/><div style="font-size: small; color: red">str</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>Display name for the environment.</div>
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
                    <b>require_comments</b>
                    <br/><div style="font-size: small; color: red">bool</div>                                                        </td>
                                <td>
                                                                                                                                                                        <ul><b>Choices:</b>
                                                                                                                                                                <li>no</li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                                                        <div>Determines if this environment requires comments for flag and segment changes.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>secure_mode</b>
                                                                            </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>Determines if this environment is in safe mode.</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>state</b>
                    <br/><div style="font-size: small; color: red">str</div>                                                        </td>
                                <td>
                                                                                                                            <ul><b>Choices:</b>
                                                                                                                                                                <li>absent</li>
                                                                                                                                                                                                <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                                                        <div>Indicate desired state of the resource</div>
                                                                                </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>tags</b>
                    <br/><div style="font-size: small; color: red">str</div>                                                        </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                                                        <div>An array of tags for this environment.</div>
                                                                                </td>
            </tr>
                        </table>
    <br/>



Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Create a new LaunchDarkly Environment
    - launchdarkly_environment:
        state: present
        project_key: "test-project-1"
        environment_key: "test_environment-1"
        color: "C9C9C9"

    # Create a new LaunchDarkly Environmnet and tag it
    - launchdarkly_environment:
        state: present
        project_key: "test-project-1"
        environment_key: "test_environment-1"
        color: "C9C9C9"
        tags: ["blue","green"]




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
                    <b>environment</b>
                    <br/><div style="font-size: small; color: red">dict</div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Return dictionary containg LaunchDarkly Environment</div>
                                        <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">{'_links': {}, '_id': '57ae15fc40cda6071f6c242e', 'key': 'production', 'name': 'Production', 'apiKey': 'XXX', 'mobileKey': 'XXX', 'color': 417505, 'defaultTtl': 0, 'secureMode': False}</div>
                                    </td>
            </tr>
                        </table>
    <br/><br/>


Status
------



This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.





.. hint::
    If you notice any issues in this documentation you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/plugins//>`_ to improve it.
