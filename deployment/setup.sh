#!/bin/bash

INASAFE_SOURCE_DIR=../src/inasafe

get_inasafe() {

    BRANCH_NAME="$1"
    echo ""
    echo "Pulling the latest InaSAFE Realtime from Github."
    echo "================================================"

    if [ ! -d ${INASAFE_SOURCE_DIR} ]
    then
        git clone --branch ${BRANCH_NAME} http://github.com/AIFDR/inasafe.git --depth 1 --verbose ${INASAFE_SOURCE_DIR}
    else
        cd ${INASAFE_SOURCE_DIR}
        git fetch origin
        git checkout ${BRANCH_NAME}
        git pull origin ${BRANCH_NAME}
        cd -
    fi
}


if [ "$1" == "checkout" ];
then
    if [ -n "$2" ];
    then
        get_inasafe "$2"
    else
        echo "ERROR: No branch name passed."
        echo "USAGE: fig run inasafe /start.sh checkout <branch_name>"
    fi
    exit
fi
