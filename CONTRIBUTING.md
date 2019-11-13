Contributing to the LaunchDarkly Ansible Collection
================================================

Submitting bug reports and feature requests
------------------

The LaunchDarkly SDK team monitors the [issue tracker](https://github.com/launchdarkly-lsbd/ansible-launchdarkly-collection/issues) in the collection repository. Bug reports and feature requests specific to this collection should be filed in this issue tracker.

Submitting pull requests
------------------

We encourage pull requests and other contributions from the community. Before submitting pull requests, ensure that all temporary or unintended code is removed. Don't worry about adding reviewers to the pull request they will automatically be added.

Build instructions
------------------

### Prerequisites

`pip install -r requirements.txt`

### Testing

You need `ansible-test` installed to run the integration tests and an API key with writer access.

`pip install ansible-test`

You can export the key as an environment variable `LAUNCHDARKLY_ACCESS_TOKEN` or write that to a file named `env.sh` under `tests/integration`.

Then change directories to `tests/integration` and run `ansible-test integration` to run through all of the tests.
