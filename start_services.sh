#!/bin/bash

read -s -p "Enter password: " password

tmux new-session -d -s temperature_logger 

tmux split-window -t temperature_logger
tmux split-window -h -t temperature_logger

tmux send-keys -t temperature_logger.1 "sudo ./logger -i2c_bus 2" ENTER
tmux send-keys -t temperature_logger.1 "$password" ENTER
tmux send-keys -t temperature_logger.0 "python webapp.py" ENTER
tmux send-keys -t temperature_logger.2 "python email_updater.py" ENTER


echo "Temperature logging services started in the background."
tmux list-sessions
