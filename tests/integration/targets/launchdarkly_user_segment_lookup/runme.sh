#!/bin/bash

set -euvx
source env.sh

ansible-playbook -vvvv test_user_segment_lookup.yml
