#!/bin/bash

program1="sudo ./logger"
program2="python email_updater.py"
program3="python webapp.py"

# Start the programs in the background
$program1 &
$program2 &
$program3 &

echo "Temperature logging services started in the background."
