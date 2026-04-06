#!/bin/bash

cd "$(dirname "$0")" || exit

if tmux has-session -t temperature_logger 2>/dev/null; then
	echo "Stopping temperature logging services..."
	tmux kill-session -t temperature_logger
	echo "Services successfully stopped."
else
	echo "Temperature logging services are not currently running."
fi