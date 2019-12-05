#!/bin/bash

# shellcheck source=tests/runme_base.sh
source "$(git rev-parse --show-toplevel)"/tests/runme_base.sh

ansible-playbook -vvvv test_variation_info.yml
