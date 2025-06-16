#!/bin/bash

#start virtual env
source "bin/activate"

# Check if the virtual environment was activated successfully
if [ $? -ne 0 ]; then
    echo "Failed to activate the virtual environment."
    exit 1
fi

#run python script
python3 /home/piod7321/DIGITAL_TWIN/gengraphllm/graphllm.py

#deactivate virtual env
deactivate

