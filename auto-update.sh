#!/bin/bash

# Auto-update script for Claire's picture frame
LOG_FILE="/home/anderson/picture-frame/update.log"
REPO_DIR="/home/anderson/picture-frame"

echo "$(date): Checking for updates..." >> $LOG_FILE

cd $REPO_DIR

# Fetch latest changes
git fetch origin main >> $LOG_FILE 2>&1

# Check if there are updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ $LOCAL != $REMOTE ]; then
    echo "$(date): Updates found! Pulling changes..." >> $LOG_FILE
    
    # Pull the changes
    git pull origin main >> $LOG_FILE 2>&1
    
    # Restart the Flask app
    echo "$(date): Restarting Flask app..." >> $LOG_FILE
    pkill -f "python3 app.py"
    sleep 2
    
    # Start the new version
    cd /home/anderson/picture-frame/web
    nohup python3 app.py > /home/anderson/flask.log 2>&1 &
    
    echo "$(date): Update complete!" >> $LOG_FILE
else
    echo "$(date): No updates available." >> $LOG_FILE
fi