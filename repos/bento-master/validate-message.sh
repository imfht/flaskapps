#!/bin/bash

set -eo pipefail

BASE="origin/master"
MAGIC="(Changes were validated by|RELEASE.[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+)?|Changelog for [0-9\.]+)"

LOG_OUTPUT=$(git log '--format=format:%B' "$BASE"..HEAD)

echo "$LOG_OUTPUT"

if [[ -z "$LOG_OUTPUT" ]]
then
  echo "No commits found"
  exit 0
else
  echo "Searching for commit message..."
  if (echo "$LOG_OUTPUT" | grep -E "$MAGIC")
  then
    exit 0
  else
    echo "No commit message found in this PR matching commit template."
    echo "To add a commit message, please run:"
    echo ""
    echo "  git commit --allow-empty --squash HEAD -t .gitmessage"
    echo ""
    exit 1
  fi
fi
