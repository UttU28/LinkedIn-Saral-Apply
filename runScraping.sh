#!/bin/bash

# Load environment variables from the .env file
export $(grep -v '^#' .env | xargs)

# Validate that necessary variables are set
if [[ -z "$CHROME_DRIVER_PATH" || -z "$CHROME_APP_PATH" || -z "$CHROME_USER_DATA_DIR" || -z "$DEBUGGING_PORT" || -z "$DATABASE_URL" ]]; then
    echo "Error: One or more environment variables are missing in the .env file."
    exit 1
fi

# Path to your Python script
PYTHON_SCRIPT="/home/robada/Desktop/LinkedIn-Saral-Apply/dataScraping.py"

# Check and kill Chrome instances running on the configured port
kill_chrome_on_port() {
    echo "Checking for Chrome instances on port $DEBUGGING_PORT..."
    chrome_pids=$(lsof -i :$DEBUGGING_PORT | awk 'NR>1 {print $2}')
    if [ -n "$chrome_pids" ]; then
        echo "Killing Chrome instances on port $DEBUGGING_PORT..."
        echo "$chrome_pids" | xargs kill -9
        echo "Chrome instances killed."
    else
        echo "No Chrome instances found on port $DEBUGGING_PORT."
    fi
}

# Check and terminate the last session of the script
terminate_previous_session() {
    echo "Checking for previous script sessions..."
    script_pid=$(pgrep -f "$PYTHON_SCRIPT")
    if [ -n "$script_pid" ]; then
        echo "Terminating previous script session with PID $script_pid..."
        kill -9 "$script_pid"
        echo "Previous script session terminated."
    else
        echo "No previous script session found."
    fi
}

# Run the Python script
run_script() {
    echo "Starting the Python script..."
    python3 "$PYTHON_SCRIPT" &
    echo "Python script started."
}

# Main execution
echo "Starting job..."
kill_chrome_on_port
terminate_previous_session
run_script
echo "Job completed. Waiting 6 hours for the next run."

# Wait 6 hours before re-running the script
sleep 6h
exec "$0"
