#!/bin/bash

set -euvx
source env.sh

ansible-playbook -vvvv test_custom_role.yml
