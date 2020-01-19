# Ansible collection for LaunchDarkly

*This version of the Ansible Collection is a **beta** version and should not be considered ready for production use while this message is visible.*

This collection provides a series of Ansible modules and plugins for interacting with [LaunchDarkly](https://www.launchdarkly.com).

LaunchDarkly overview
-------------------------
[LaunchDarkly](https://www.launchdarkly.com) is a feature management platform that serves over 100 billion feature flags daily to help teams build better software, faster. [Get started](https://docs.launchdarkly.com/docs/getting-started) using LaunchDarkly today!

[![Twitter Follow](https://img.shields.io/twitter/follow/launchdarkly.svg?style=social&label=Follow&maxAge=2592000)](https://twitter.com/intent/follow?screen_name=launchdarkly)

## Requirements

- ansible version >= 2.9
- launchdarkly-api >= 2.0.24
- dictdiffer == 0.8.0

## Installation

```
ansible-galaxy collection install launchdarkly_labs.collection
```

You will then need to install the library dependencies. The requirements.txt will be in the directory that Ansible installed your collection to. Default is `~/.ansible/collections`

```
python -m pip install -r ~/.ansible/collections/ansible_collections/launchdarkly_labs/collection/requirements.txt
```

## Usage

To use a module from LaunchDarkly collection, please reference the full namespace, collection name, and modules name that you want to use:

```yaml
---
- name: Using LaunchDarkly collection
  hosts: localhost
  tasks:
    - launchdarkly_labs.collection.launchdarkly_feature_flag:
        name: example
        kind: bool
        state: present
        temporary: false
        key: example_flag_creation
```

Or you can add full namespace and collection name in the `collections` element:

```yaml
---
- name: Using LaunchDarkly collection
  hosts: localhost
  collections:
    - launchdarkly_labs.collection
  tasks:
    - launchdarkly_feature_flag:
        name: example
        kind: bool
        state: present
        temporary: false
        key: example_flag_creation
```

## Resource Supported

- launchdarkly_feature_flag - Create, update, delete a LaunchDarkly Feature Flag
- launchdarkly_feature_flag_environment - Configure an Environment specific LaunchDarkly Feature Flag
- launchdarkly_feature_flag_sync - Sync flag settings across environments
- launchdarkly_custom_role - Create, update, delete a LaunchDarkly Custom Role
- launchdarkly_environment - Create, update, delete a LaunchDarkly Project Environment
- launchdarkly_project - Create, update, delete a LaunchDarkly Project
- launchdarkly_project_copy - Copy a LaunchDarkly Project
- launchdarkly_test_generator - Generate a LaunchDarkly compatible SDK test file
- launchdarkly_user_segment - Create, update, delete a LaunchDarkly User Segment
- launchdarkly_user_segment_sync - Copy a LaunchDarkly User Segment across Environments
- launchdarkly_variation_info - Return a value from a feature flag evaluation
- launchdarkly_webhook - Create, update, delete a LaunchDarkly Webhook

## Lookups Support
- launchdarkly_environment - Lookup a specific LaunchDarkly Environment
- launchdarkly_user_segment - Lookup a specific LaunchDarkly User Segment in an Environment

Contributing
------------

We encourage pull requests and other contributions from the community. Check out our [contributing guidelines](CONTRIBUTING.md) for instructions on how to contribute to this SDK.

About LaunchDarkly
-----------

* LaunchDarkly is a continuous delivery platform that provides feature flags as a service and allows developers to iterate quickly and safely. We allow you to easily flag your features and manage them from the LaunchDarkly dashboard.  With LaunchDarkly, you can:
    * Roll out a new feature to a subset of your users (like a group of users who opt-in to a beta tester group), gathering feedback and bug reports from real-world use cases.
    * Gradually roll out a feature to an increasing percentage of users, and track the effect that the feature has on key metrics (for instance, how likely is a user to complete a purchase if they have feature A versus feature B?).
    * Turn off a feature that you realize is causing performance problems in production, without needing to re-deploy, or even restart the application with a changed configuration file.
    * Grant access to certain features based on user attributes, like payment plan (eg: users on the ‘gold’ plan get access to more features than users in the ‘silver’ plan). Disable parts of your application to facilitate maintenance, without taking everything offline.
* LaunchDarkly provides feature flag SDKs for a wide variety of languages and technologies. Check out [our documentation](https://docs.launchdarkly.com/docs) for a complete list.
* Explore LaunchDarkly
    * [launchdarkly.com](https://www.launchdarkly.com/ "LaunchDarkly Main Website") for more information
    * [docs.launchdarkly.com](https://docs.launchdarkly.com/  "LaunchDarkly Documentation") for our documentation and SDK reference guides
    * [apidocs.launchdarkly.com](https://apidocs.launchdarkly.com/  "LaunchDarkly API Documentation") for our API documentation
    * [blog.launchdarkly.com](https://blog.launchdarkly.com/  "LaunchDarkly Blog Documentation") for the latest product updates
    * [Feature Flagging Guide](https://github.com/launchdarkly/featureflags/  "Feature Flagging Guide") for best practices and strategies
