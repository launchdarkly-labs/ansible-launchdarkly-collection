#!/bin/bash
# https://github.com/lotharschulz/sphinx-pages
set -euo pipefail
IFS=$'\n\t'

buildDirectory=_build

# get a clean master branch assuming
git checkout master
git pull origin master
git clean -df
git checkout -- .
git fetch --all

# build html docs from sphinx files
sphinx-build -b html docs/source "$buildDirectory"

# create or use orphaned gh-pages branch
branch_name=gh-pages
if [ "$(git branch --list "$branch_name")" ]
then
	git stash --all
	git checkout $branch_name
	git pull origin $branch_name
	git stash apply && :
	git checkout stash -- . && : # force git stash to overwrite added files
else
	git checkout --orphan "$branch_name"
fi

if [ -d "$buildDirectory" ]
then
    for f in ./*
    do
    case $f in
        *_build) true;;
        *) rm -rf "$f";;
    esac
    done
	mv "${buildDirectory}"/* . && rm -rf "${buildDirectory}"
	touch .nojeykll
	git add .
	git commit -m "new pages version $(date)"
	git push origin gh-pages
else
	echo "directory $buildDirectory does not exists"
fi
