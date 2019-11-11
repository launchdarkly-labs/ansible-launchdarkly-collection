#!/bin/bash

set -euvx
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
