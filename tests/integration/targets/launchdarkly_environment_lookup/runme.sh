#!/bin/bash

set -euvx
source env.sh

ansible-playbook -vvvv test_environment_lookup.yml
