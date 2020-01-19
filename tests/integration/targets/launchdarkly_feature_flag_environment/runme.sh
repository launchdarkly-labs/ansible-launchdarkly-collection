#!/bin/bash

FILE=test_feature_flag_environment.yml
if [ ! -z "$LAUNCHDARKLY_ACCESS_TOKEN" ] && [ ! -z "$LAUNCHDARKLY_DEST_ACCESS_TOKEN" ] && [ ! -z "$LAUNCHDARKLY_SDK_KEY" ];
then
    ansible-playbook -vvvv ${FILE}
elif [[ -f vars.yml ]]
then
    ansible-playbook -vvvv ${FILE} --extra-vars "@vars.yml"
else
    envdir="$(git rev-parse --show-toplevel)"
    filename=env.sh

    if [[ -z "${envdir}" ]]
    then
    echo "Not in git repository."
    exit 1
    fi

    file="$(find "${envdir}" -name "${filename}" -type f -print -quit)"

    if [[ -z "${file}" ]]
    then
    echo "Source file: env.sh not found."
    exit 1
    fi

    # shellcheck disable=SC1090
    source "${file}"
    ansible-playbook -vvvv ${FILE} --extra-vars "ld_api_key=${LAUNCHDARKLY_ACCESS_TOKEN}"
fi
