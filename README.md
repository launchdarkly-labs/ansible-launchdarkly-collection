> This project is not officially supported by LaunchDarkly.

# Ansible collection for LaunchDarkly

*This version of the Ansible collection is a **beta** version and should not be considered ready for production use while this message displays.*

This collection provides a series of Ansible modules and plugins for interacting with [LaunchDarkly](https://www.launchdarkly.com).

## Documentation

Additional documentation is available: [LaunchDarkly Ansible collection](https://launchdarkly-labs.github.io/ansible-launchdarkly-collection/).

## Requirements

To use the modules and plugins in this collection, you need:

- ansible version >= 2.9
- launchdarkly-api >= 2.0.24
- dictdiffer == 0.8.0

## Installation

To install this collection, use:

```
ansible-galaxy collection install launchdarkly_labs.collection
```

Then, install the library dependencies. These are listed in `requirements.txt`, which is in the directory where Ansible installed your collection. By default, this is `~/.ansible/collections`.

To install the library dependencies, use:

```
python -m pip install -r ~/.ansible/collections/ansible_collections/launchdarkly_labs/collection/requirements.txt
```

## Usage

To use a module from the Ansible collection, reference the full namespace, collection name, and module name that you want to use. Here's how:

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

Alternatively, you can specify the full namespace and collection name in the `collections` element:

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

## Resources supported

The LaunchDarkly Ansible collection supports the following resources:

- `launchdarkly_custom_role`: Manage custom roles
- `launchdarkly_environment`: Manage environments for a given project
- `launchdarkly_feature_flag`: Manage feature flags
- `launchdarkly_feature_flag_environment`: Configure environment-specific flag targeting
- `launchdarkly_feature_flag_info`: Return a list of feature flags
- `launchdarkly_feature_flag_sync`: Sync flag settings across environments
- `launchdarkly_feature_flag_validator`: Validate feature flags by running a configuration test
- `launchdarkly_project`: Manage projects
- `launchdarkly_project_copy`: Copy a project
- `launchdarkly_project_info`: Return a list of projects
- `launchdarkly_test_generator`: Create a JSON file for local testing with a LaunchDarkly SDK
- `launchdarkly_user_segment`: Manage user segments
- `launchdarkly_user_segment_sync`: Copy a user segment across environments
- `launchdarkly_variation_info`: Return the value from a feature flag evaluation
- `launchdarkly_webhook`: Manage LaunchDarkly webhooks

## Lookups Support

The LaunchDarkly Ansible collection supports the following lookups:

- `launchdarkly_environment`: Look up a specific environment
- `launchdarkly_user_segment`: Look up a specific user segment

LaunchDarkly overview
-------------------------
[LaunchDarkly](https://www.launchdarkly.com) is a feature management platform that serves over 100 billion feature flags daily to help teams build better software, faster. [Get started](https://docs.launchdarkly.com/docs/getting-started) using LaunchDarkly today!

[![Follow us on Twitter](https://img.shields.io/twitter/follow/launchdarkly.svg?style=social&label=Follow&maxAge=2592000)](https://twitter.com/intent/follow?screen_name=launchdarkly)

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
