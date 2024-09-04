#!/bin/bash

screen -X -S temperature_logger quit
screen -X -S email_updater quit
screen -X -S webapp quit
screen -wipe

echo "Temperature logger services killed."
