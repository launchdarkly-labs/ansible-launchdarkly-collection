# Ansible collection for LaunchDarkly

This collection provides a series of Ansible modules and plugins for interacting with [LaunchDarkly](https://www.launchdarkly.com).

## Requirements

- ansible version >= 2.9

## Installation

```
ansible-galaxy collection install launchdarkly.collection
```

## Usage

To use a module from LaunchDarkly collection, please reference the full namespace, collection name, and modules name that you want to use:

```yaml
---
- name: Using LaunchDarkly collection
  hosts: localhost
  tasks:
    - launchdarkly.collection.launchdarkly_feature_flag:
        name: "example"
        kind: "bool"
        state: present
        temporary: false
        key: "example_flag_creation"
```

Or you can add full namepsace and collecton name in the `collections` element:

```yaml
---
- name: Using LaunchDarkly collection
  hosts: localhost
  collections:
    - launchdarkly.collection
  tasks:
    - launchdarkly_feature_flag:
        name: "example"
        kind: "bool"
        state: present
        temporary: false
        key: "example_flag_creation"
```

## Resource Supported

- launchdarkly_feature_flag - Create, update, delete a LaunchDarkly Feature Flag
- launchdarkly_custom_role - Create, update, delete a LaunchDarkly Custom Role
- launchdarkly_environment - Create, update, delete a LaunchDarkly Project Environment
- launchdarkly_project - Create, update, delete a LaunchDarkly Project
- launchdarkly_user_segment - Create, update, delete a LaunchDarkly User Segment
- launchdarkly_webhook - Create, update, delete a LaunchDarkly Webhook



## Lookups Support
- launchdarkly_environment - Lookup a specific LaunchDarkly Environment
