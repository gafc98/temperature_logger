#!/bin/bash
if tmux has-session -t temperature_logger; then
    tmux kill-ses -t temperature_logger
    echo "Temperature logger services killed."
else
    echo "Temperature logging services are not running."
fi
