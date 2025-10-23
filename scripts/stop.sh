#!/bin/bash

# Find and kill the process on port 8888
PID=$(lsof -ti:8888 2>/dev/null)

if [ -z "$PID" ]; then
    echo "No VLLM service found on port 8888. Nothing to stop."
else
    echo "Stopping VLLM service (PID: $PID)..."
    kill -TERM "$PID"
    sleep 5
    if kill -0 "$PID" 2>/dev/null; then
        echo "Process didn't stop gracefully. Forcibly killing it."
        kill -KILL "$PID"
    fi
    echo "VLLM service stopped."
fi
