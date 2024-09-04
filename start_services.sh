#!/bin/bash

read -s -p "Enter password: " password

screen -dmS temperature_logger sudo ./logger
sleep 1
screen -S temperature_logger -p 0 -X stuff "$password^M"

screen -dmS email_updater python email_updater.py
screen -dmS webapp python webapp.py

echo "Temperature logging services started in the background."
