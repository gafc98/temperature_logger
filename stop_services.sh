#!/bin/bash

sudo killall logger
screen -X -S email_updater quit
screen -X -S webapp quit

echo "Temperature logger services killed."
