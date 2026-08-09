#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")" || exit

if tmux has-session -t temperature_logger 2>/dev/null; then
	echo "Temperature logging services are already running."
else
	tmux new-session -d -s temperature_logger 
	tmux split-window -t temperature_logger
	tmux split-window -h -t temperature_logger
	
	# Start the C++ logger (using full path to binary for sudo safety)
	tmux send-keys -t temperature_logger.1 "sudo $(pwd)/logger -i2c_bus 2" ENTER

	# Run Python scripts directly using the venv interpreter
	tmux send-keys -t temperature_logger.0 "./venv/bin/python webapp.py" ENTER
	tmux send-keys -t temperature_logger.2 "./venv/bin/python email_updater.py" ENTER

	echo "Temperature logging services started in the background."
	tmux list-sessions
fi