#!/bin/bash

post ()
{
    local topic="$1"
    shift
    local Msg="$*"
    mosquitto_pub -h "$AWSIP" -p "$AWSPORT" -t "$topic" -m "$Msg"
}

export DATE=$(date +%Y-%m-%d.%H:%M)
post status/eaws/logout "User: $NR_USER Date: $DATE"
