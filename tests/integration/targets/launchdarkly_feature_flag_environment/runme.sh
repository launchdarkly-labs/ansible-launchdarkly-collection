#!/bin/bash

set -euvx
source env.sh

ansible-playbook -vvvv test_feature_flag_environment.yml
#ansible-playbook -vvvv test_feature_flag_environment_chatbox.yml
