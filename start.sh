#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Kill existing server on port 8000
echo "Stopping existing server..."
fuser -k 8000/tcp 2>/dev/null || true
pkill -f "server.py" 2>/dev/null || true

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if missing
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start server
echo "Starting server..."
echo "Open http://localhost:8000 in your browser"
python3 server.py
