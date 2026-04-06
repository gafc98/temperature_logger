#!/bin/bash

cd "$(dirname "$0")" || exit

if tmux has-session -t temperature_logger 2>/dev/null; then
	echo "Temperature logging services are already running."
else
	tmux new-session -d -s temperature_logger 
	tmux split-window -t temperature_logger
	tmux split-window -h -t temperature_logger
	
	# Start the logger (use visudo to make process passwordless)
	tmux send-keys -t temperature_logger.1 "sudo ./logger -i2c_bus 2" ENTER

	tmux send-keys -t temperature_logger.0 "python webapp.py" ENTER
	tmux send-keys -t temperature_logger.2 "python email_updater.py" ENTER

	echo "Temperature logging services started in the background."
	tmux list-sessions
fi