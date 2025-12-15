#!/bin/bash

# Kill existing server on port 8000 or by name
echo "Stopping existing server..."
fuser -k 8000/tcp 2>/dev/null || true
pkill -f "python3 /root/projects/ParseClipmate/server.py" || true

# Install dependencies if missing
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Installing dependencies..."
    pip install fastapi uvicorn
fi

# Run parser to ensure DB is up to date
echo "Running parser..."
python3 /root/projects/ParseClipmate/main.py

# Start server
echo "Starting server..."
echo "Open http://localhost:8000 in your browser"
python3 /root/projects/ParseClipmate/server.py
