#!/bin/bash

# Quick start script for local development

echo "Starting Cross-Chain USDC Payment Gateway..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies if needed
if ! python -c "import flask" &> /dev/null; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Starting servers..."
echo "Backend will run on http://localhost:5000"
echo "Frontend will run on http://localhost:3000"
echo ""

# Start backend in background
cd api && python server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
cd .. && npm run dev &
FRONTEND_PID=$!

echo "Servers started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

