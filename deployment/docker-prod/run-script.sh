#!/bin/bash

# Execute this script after it is sourced

echo "Current directory `pwd`"

source run-env-linux.sh /usr

# Add python plugins to path

export PYTHONPATH=$PYTHONPATH:/usr/share/qgis/python/plugins/
export InaSAFEQGIS=/home/inasafe/src/inasafe

if [ $1=="inasafe" ]; then
    eval "xvfb-run -a --server-args=\"-screen 0, 1024x768x24\" inasafe $2"
else
    xvfb-run -a --server-args="-screen 0, 1024x768x24" python "/helper_script/$1.py"
fi
