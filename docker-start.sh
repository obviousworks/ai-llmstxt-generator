#!/bin/bash
set -e

echo "=========================================="
echo "Starting LLMs.txt Generator"
echo "=========================================="

# Create log directory if it doesn't exist
mkdir -p /app/logs

# Start Backend API
echo "Starting Backend API on port 8000..."
cd /app/backend
python3 run_dev.py > /app/logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        exit 1
    fi
    sleep 1
done

# Start Frontend
echo "Starting Frontend on port 3000..."
cd /app/frontend
npm start > /app/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo "=========================================="
echo "✅ LLMs.txt Generator is running!"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3005"
echo "Logs: /app/logs/"
echo "=========================================="

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap SIGTERM and SIGINT
trap shutdown SIGTERM SIGINT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
