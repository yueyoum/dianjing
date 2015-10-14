#!/bin/bash

OPT=""
QUERY=""

function error {
    echo "ERROR PARAMS"
    exit 1
}


if [[ -z $1 ]]
then
    error
else
    if [[ -z $2 ]]
    then
        QUERY="$1"
    else
        OPT="$1"
        QUERY="$2"
    fi
fi

grep $OPT "$QUERY" --color -n * -r --exclude-dir=env --exclude-dir=tests --exclude-dir=protomsg --exclude-dir=protobuf --exclude-dir=static --exclude-dir=run --exclude=\*.pyc

