#!/bin/bash


if [[ -z "$LAUNCHDARKLY_ACCESS_TOKEN" ]] &&
   [[ -z "$LAUNCHDARKLY_DEST_ACCESS_TOKEN" ]] &&
   [[ -z "$LAUNCHDARKLY_SDK_KEY" ]]
then
    :
else
    # shellcheck source=tests/runme_base.sh
    source "$(git rev-parse --show-toplevel)"/tests/runme_base.sh
fi




ansible-playbook -vvvv test_custom_role.yml
