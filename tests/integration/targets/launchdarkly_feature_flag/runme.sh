#!/bin/bash

set -euvx
source env.sh

ansible-playbook -vvvv test_feature_flag.yml
