#!/usr/bin/env bash

function get_current_coverage {
    local prev_stat_raw=`TEST_DB_URI=${TEST_DB_URI} tox -e py35-functional | grep TOTAL | awk '{print $4}'`
    echo ${prev_stat_raw:0:2}
}

function get_coverage_delta {
    local current_coverage=$(get_current_coverage)
    local current_branch=`git branch | awk '{print $2}'`
    git checkout `git rev-parse --verify HEAD^${1:-1}`
    local prev_coverage=$(get_current_coverage)
    if [ "${prev_coverage}" -gt "${current_coverage}" ]; then
        echo -e "Test regression found.\n Current commit: ${current_coverage} \Previous commit: ${prev_coverage}."
        git checkout ${current_branch}
        exit 1
    fi
    git checkout ${current_branch}
}


get_coverage_delta ${1:-1}
