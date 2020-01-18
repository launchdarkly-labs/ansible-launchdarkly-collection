#!/bin/bash

FILE=test_feature_flag.yml
if [[ -v "$LAUNCHDARKLY_ACCESS_TOKEN" ]] && [[ -v "$LAUNCHDARKLY_DEST_ACCESS_TOKEN" ]] && [[ -v "$LAUNCHDARKLY_SDK_KEY" ]];
then
    ansible-playbook -vvvv ${FILE}
elif [[ -f vars.yml ]]
then
    ansible-playbook -vvvv ${FILE} --extra-vars "@vars.yml"
else
    echo "You need to have Environment Variables: LAUNCHDARKLY_ACCESS_TOKEN, LAUNCHDARKLY_DEST_ACCESS_TOKEN, LAUNCHDARKLY_SDK_KEY"
    exit 1
fi
