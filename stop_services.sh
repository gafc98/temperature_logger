#!/bin/bash

program1="logger"
program2_py="email_updater.py"
program3_py="webapp.py"

# Kill the programs
killall $program1
killall python
killall $program2_py
killall $program3_py

echo "Temperature logger services killed."
