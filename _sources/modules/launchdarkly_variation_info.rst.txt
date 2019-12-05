:source: 


.. _launchdarkly_variation_info_:


launchdarkly_variation_info -- Return value from Feature Flag Evaluation
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 0.2.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Return value from Feature Flag Evaluation




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
                    <b>flag_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>Display name for the environment.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>sdk_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">"default"</div>
                                    </td>
                                <td>
                                            <div>Environment SDK key for evaluation to run against. May be set as <code>LAUNCHDARKLY_SDK_KEY</code> environment variable.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>user</b>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>A list of Environments to create. Cannot be updated with this resource.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
    # Create a new LaunchDarkly Project with tags
    - launchdarkly_variation_info:
        sdk_key: sdk-12345
        flag_key: example-test-flag
        user:
            key: aabbccdd
            custom:
                test-attribute: green
                plan: free




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
                    <b>is_default_value</b>
                    <div style="font-size: small">
                      <span style="color: purple">boolean</span>
                                          </div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Is it the default value in code.</div>
                                        <br/>
                                    </td>
            </tr>
                                <tr>
                                <td colspan="1">
                    <b>reason</b>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Why was that specific value returned.</div>
                                        <br/>
                                    </td>
            </tr>
                                <tr>
                                <td colspan="1">
                    <b>type</b>
                    <div style="font-size: small">
                      <span style="color: purple">string</span>
                                          </div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Type of return value</div>
                                        <br/>
                                    </td>
            </tr>
                                <tr>
                                <td colspan="1">
                    <b>value</b>
                    <div style="font-size: small">
                      <span style="color: purple">-</span>
                                          </div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Value returned from variation. Type is set in <code>type</code> return.</div>
                                        <br/>
                                    </td>
            </tr>
                                <tr>
                                <td colspan="1">
                    <b>variation_index</b>
                    <div style="font-size: small">
                      <span style="color: purple">integer</span>
                                          </div>
                                    </td>
                <td>always</td>
                <td>
                                            <div>Index value of variation.</div>
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
