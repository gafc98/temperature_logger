#!/bin/bash

sudo ./logger &
screen -dmS email_updater python email_updater.py
screen -dmS webapp python webapp.py

echo "Temperature logging services started in the background."
