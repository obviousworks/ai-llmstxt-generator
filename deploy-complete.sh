#!/bin/bash
# Complete deployment script for LLM.txt Generator

echo "🚀 Starting LLM.txt Generator Deployment..."
echo "==========================================="

# Stop any existing services
echo "Stopping existing services..."
pkill -f "python.*run_dev.py" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true

# Start backend
echo "Starting backend..."
cd backend
python3 run_dev.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "Starting frontend..."
PORT=5001 npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 10

# Check if frontend is running
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ Frontend started successfully"
else
    echo "❌ Frontend failed to start"
    exit 1
fi

echo ""
echo "🌐 Services running:"
echo "   Frontend: http://localhost:5001"
echo "   Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
