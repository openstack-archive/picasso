#!/usr/bin/env bash

set +x
set +e

function get_current_coverage {
    local prev_stat_raw=`pytest --tb=long --capture=sys --cov=laos --capture=fd laos/tests/${1:-functional} | grep TOTAL | awk '{print $4}'`
    echo ${prev_stat_raw:0:2}
}

function get_coverage_delta {
    local current_coverage=$(get_current_coverage $1)
    local current_branch=`git branch | awk '{print $2}'`
    echo -e "Falling back to ${2} commits."
    local commits=`seq  -f "^" -s '' ${2}`
    git checkout `git rev-parse --verify HEAD${commits}` &> /dev/null
    local prev_coverage=$(get_current_coverage $1)
    echo -e "Current coverage: ${current_coverage}%"
    echo -e "Previous coverage: ${prev_coverage}%"
    if [ "${prev_coverage}" -gt "${current_coverage}" ]; then
        echo -e "Failed: test regression found.\n Current commit: ${current_coverage} \Previous commit: ${prev_coverage}."
        git checkout ${current_branch}
        exit 1
    fi
    echo -e "Passed: regression not found."
    git checkout ${current_branch} &> /dev/null
}


get_coverage_delta ${1:-functional} ${2:-1}
