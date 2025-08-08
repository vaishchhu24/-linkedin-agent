#!/bin/bash

# LinkedIn Workflow Auto-Start Script
# This script is called by launchd to start the workflow

cd /Users/vaishnavisingh/Downloads/linkedin_agent

# Start the workflow in background
nohup python3 background_workflow_system.py start > background_workflow.log 2>&1 &

# Save the PID
echo $! > background_workflow.pid

exit 0 