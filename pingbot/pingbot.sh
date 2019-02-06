#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

function slack-notify {
    CONTENT="Site "${1}" seems to be down!"
    curl -X POST -H 'Content-type: application/json' \
         --data "{\"text\":\"${CONTENT}\"}" \
         $SLACK_WEBHOOK_URL
}

function verify {
    echo verifying $1
    set +e
    curl -sSfL $1 > /dev/null
    if [ ! $? -eq 0 ]; then
        set -e
        slack-notify $1
    fi
}

pushd $(dirname $0)
for each in $(cat domains.txt); do
    verify $each
done
popd
