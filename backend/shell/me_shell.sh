#!/bin/bash
# Shell entrypoint for command execution
# Usage: ./me_shell.sh <command_id>

# Check if command_id is provided
if [ $# -eq 0 ]; then
    echo "Error: command_id is required" >&2
    exit 1
fi

COMMAND_ID="$1"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Execute the Python shell dispatcher
cd "$SCRIPT_DIR"
python me_shell.py "$COMMAND_ID"
