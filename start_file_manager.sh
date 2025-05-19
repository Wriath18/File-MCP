#!/bin/bash

# Start the File System Manager application
cd "$(dirname "$0")" || exit
cd /app/backend

# Check if streamlit is already running
if pgrep -f "streamlit run file_manager.py" > /dev/null; then
    echo "File System Manager is already running."
    echo "You can access it at: http://localhost:8501"
else
    echo "Starting File System Manager..."
    streamlit run file_manager.py > streamlit_app.log 2>&1 &
    echo "File System Manager is running."
    echo "You can access it at: http://localhost:8501"
fi