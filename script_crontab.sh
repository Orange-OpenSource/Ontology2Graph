#!/bin/bash

#start virtual env
source "/home/pdooze/DIGITAL_TWIN/gengraphllm/bin/activate"

# Check if the virtual environment was activated successfully
if [ $? -ne 0 ]; then
    echo "Failed to activate the virtual environment."
    exit 1
fi

#run python script
/home/pdooze/DIGITAL_TWIN/gengraphllm/bin/python3 /home/pdooze/DIGITAL_TWIN/gengraphllm/graphllm.py

#deactivate virtual env
deactivate

