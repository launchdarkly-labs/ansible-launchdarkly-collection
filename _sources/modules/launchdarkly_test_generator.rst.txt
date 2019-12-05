:source: 


.. _launchdarkly_test_generator_:


launchdarkly_test_generator -- Create a JSON file for testing
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 0.2.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create a JSON file for local testing




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
                    <b>environment_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>A unique key that will be used to reference the flag in your code.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>overrides_flag</b>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>override specific keys</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>project_key</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">"default"</div>
                                    </td>
                                <td>
                                            <div>Project key will group flags together.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
    # Create a new LaunchDarkly Project with tags
      - name: Generate Test JSON
        launchdarkly_test_generator:
          sdk_key: sdk-test-123456
          overrides_flag:
            - example_test_flag: True
        register: results




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
                    <b>content</b>
                    <div style="font-size: small">
                      <span style="color: purple">json</span>
                                          </div>
                                    </td>
                <td>on success</td>
                <td>
                                            <div>Dictionary containing a JSON object that can be used as a file source.</div>
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
