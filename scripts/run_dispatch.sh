#!/bin/bash

# Go to project scripts directory
cd /Users/praveenchaudhary/Desktop/Order-Management/scripts || exit

# Activate Python virtual environment
source /Users/praveenchaudhary/Desktop/Order-Management/venv/bin/activate

# Export email credentials (can also be set in your OS keychain or .bash_profile for security)
export EMAIL_USER="pkc05@yahoo.com"
export EMAIL_PASSWORD="jitowwvlxajpsxbp"

# Run the dispatch report script
python email_dispatch_report.py
