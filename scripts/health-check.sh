#!/bin/bash
# LLMs.txt Generator - Health Check Script
# Monitors services and restarts if needed

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
LOG_FILE="${LOG_FILE:-/var/log/llms-generator/health-check.log}"
USE_SYSTEMD=true  # Set to false if using Docker

# Create log directory if needed
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a "$LOG_FILE"
}

# Function to check service health
check_service() {
    local service_name="$1"
    local url="$2"
    local timeout=5
    
    if curl -sf --max-time $timeout "$url" > /dev/null 2>&1; then
        return 0  # Service is healthy
    else
        return 1  # Service is down
    fi
}

# Function to restart systemd service
restart_systemd_service() {
    local service="$1"
    log_message "⚠️  Restarting systemd service: $service"
    
    if sudo systemctl restart "$service" 2>&1 | tee -a "$LOG_FILE"; then
        log_message "✅ Service restarted successfully: $service"
        return 0
    else
        log_message "❌ Failed to restart service: $service"
        return 1
    fi
}

# Function to restart Docker container
restart_docker_container() {
    local container="$1"
    log_message "⚠️  Restarting Docker container: $container"
    
    if docker restart "$container" 2>&1 | tee -a "$LOG_FILE"; then
        log_message "✅ Container restarted successfully: $container"
        return 0
    else
        log_message "❌ Failed to restart container: $container"
        return 1
    fi
}

# Main health check
log_message "🔍 Starting health check..."

# Check Backend API
if ! check_service "Backend API" "$API_URL/health"; then
    log_message "❌ Backend API is down!"
    
    if [ "$USE_SYSTEMD" = true ]; then
        restart_systemd_service "llms-api.service"
    else
        restart_docker_container "llms-txt-generator"
    fi
    
    # Wait and verify
    sleep 10
    if check_service "Backend API" "$API_URL/health"; then
        log_message "✅ Backend API is now healthy"
    else
        log_message "❌ Backend API still unhealthy after restart"
    fi
else
    log_message "✅ Backend API is healthy"
fi

# Check Frontend
if ! check_service "Frontend" "$FRONTEND_URL"; then
    log_message "❌ Frontend is down!"
    
    if [ "$USE_SYSTEMD" = true ]; then
        restart_systemd_service "llms-frontend.service"
    else
        # Docker container includes both services
        if [ "$USE_SYSTEMD" = false ]; then
            log_message "ℹ️  Frontend is part of Docker container (already restarted)"
        fi
    fi
    
    # Wait and verify
    sleep 10
    if check_service "Frontend" "$FRONTEND_URL"; then
        log_message "✅ Frontend is now healthy"
    else
        log_message "❌ Frontend still unhealthy after restart"
    fi
else
    log_message "✅ Frontend is healthy"
fi

log_message "🏁 Health check completed"
