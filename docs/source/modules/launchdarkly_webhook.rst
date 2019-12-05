:source: 


.. _launchdarkly_webhook_:


launchdarkly_webhook -- Manage LaunchDarkly Webhooks
++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 0.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manage LaunchDarkly Webhooks




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
                    <b>enabled</b>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>no</li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                            <div>Whether this webhook is enabled or not.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>name</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>A human-readable name for your webhook.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>secret</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>If sign is true, and the secret attribute is omitted, LaunchDarkly will automatically generate a secret for you.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>sign</b>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>no</li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                            <div>If sign is false, the webhook will not include a signature header, and the secret can be omitted.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>state</b>
                    <div style="font-size: small">
                        <span style="color: purple">-</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>absent</li>
                                                                                                                                                                                                <li><div style="color: blue"><b>present</b>&nbsp;&larr;</div></li>
                                                                                    </ul>
                                                                            </td>
                                <td>
                                            <div>Indicate desired state of the resource.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>url</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>The URL of the remote webhook.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="1">
                    <b>webhook_id</b>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                <td>
                                            <div>Webhook id. Required when updating resource.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
    # Create a new LaunchDarkly Webhook
    - launchdarkly_webhook:
        state: present
        project_key: test-project-1
        environment_key: test-environment-1
        user_segment_key: test-key-1
        name: "Test Segment"
        description: "This is a testing segment"
        rules:
            clauses:
              - attribute: testAttribute
                op: contains
                values:
                  - 2
                  - 3
                negate: true
        tags:
          - blue
          - green
        included:
          - test1
          - test2
        excluded:
          - test3
          - test4




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
                    <b>webhook</b>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>on success</td>
                <td>
                                            <div>Dictionary containing a <a href='https://github.com/launchdarkly/api-client-python/blob/2.0.24/docs/Webhook.md'>Webhook</a></div>
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
