#!/usr/bin/env bash

set -e

status_code=$(curl --write-out %{http_code} --silent --output /dev/null -X POST -H "Content-Type:application/json" -d '{
	"routing_key": "TESTTESTTESTTEST",
	"event_action": "test",
	"payload": {
		"summary": "Important build on circle is failing that should not fail",
		"severity": "error",
		"source": "CircleCI"
	}
}' https://events.pagerduty.com/v2/enqueue)

if [[ "$status_code" -ne 202 ]]; then
    echo "Sending to pagerduty failed! Status code: $status_code"
    exit 1
else
    echo "Sent to pagerduty successfully"
    exit 0
fi
