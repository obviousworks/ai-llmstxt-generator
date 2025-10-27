#!/bin/bash

# LLMs.txt Generator Health Check & Auto-Restart Script
# This script checks if the services are running and restarts them if needed

# Configuration
PROJECT_DIR="/opt/ai-llmstxt-generator"
LOG_FILE="/var/log/llm-txt-healthcheck.log"
FRONTEND_PORT=5001
BACKEND_PORT=8000
FRONTEND_URL="http://localhost:5001/llm-text-generator"
BACKEND_URL="http://localhost:8000/docs"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if a port is listening
check_port() {
    local port=$1
    netstat -tuln | grep -q ":${port} "
    return $?
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null)
    if [ "$response" = "200" ]; then
        return 0
    else
        return 1
    fi
}

# Function to stop all services
stop_services() {
    log "Stopping all services..."
    pkill -9 -f "next"
    pkill -9 -f "uvicorn"
    sleep 2
}

# Function to start services
start_services() {
    log "Starting services..."
    cd "$PROJECT_DIR" || exit 1
    
    # Start Backend
    log "Starting backend..."
    cd backend
    source venv/bin/activate
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 600 >> "$LOG_FILE" 2>&1 &
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Start Frontend (Production)
    log "Starting frontend..."
    NODE_ENV=production npm run start -- --port 5001 >> "$LOG_FILE" 2>&1 &
    
    # Wait for frontend to start
    sleep 5
    
    log "Services started"
}

# Main health check logic
log "=== Health Check Started ==="

# Check if processes are running
FRONTEND_RUNNING=false
BACKEND_RUNNING=false

if check_port $FRONTEND_PORT; then
    FRONTEND_RUNNING=true
    log "Frontend port $FRONTEND_PORT is listening"
else
    log "WARNING: Frontend port $FRONTEND_PORT is NOT listening"
fi

if check_port $BACKEND_PORT; then
    BACKEND_RUNNING=true
    log "Backend port $BACKEND_PORT is listening"
else
    log "WARNING: Backend port $BACKEND_PORT is NOT listening"
fi

# Check HTTP endpoints
FRONTEND_HEALTHY=false
BACKEND_HEALTHY=false

if $FRONTEND_RUNNING; then
    if check_http "$FRONTEND_URL"; then
        FRONTEND_HEALTHY=true
        log "Frontend HTTP check: OK"
    else
        log "ERROR: Frontend HTTP check FAILED"
    fi
fi

if $BACKEND_RUNNING; then
    if check_http "$BACKEND_URL"; then
        BACKEND_HEALTHY=true
        log "Backend HTTP check: OK"
    else
        log "ERROR: Backend HTTP check FAILED"
    fi
fi

# Decide if restart is needed
RESTART_NEEDED=false

if ! $FRONTEND_HEALTHY || ! $BACKEND_HEALTHY; then
    log "Services are unhealthy - restart needed"
    RESTART_NEEDED=true
fi

# Restart if needed
if $RESTART_NEEDED; then
    log "=== RESTARTING SERVICES ==="
    stop_services
    start_services
    
    # Verify restart was successful
    sleep 10
    if check_http "$FRONTEND_URL" && check_http "$BACKEND_URL"; then
        log "=== RESTART SUCCESSFUL ==="
    else
        log "=== RESTART FAILED - Manual intervention required ==="
    fi
else
    log "=== All services healthy ==="
fi

log "=== Health Check Completed ==="
echo ""
