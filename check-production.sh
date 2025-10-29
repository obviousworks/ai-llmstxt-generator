#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🔍 LLMs.txt Generator - Production Status Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check running processes
echo -e "${YELLOW}📊 Running Processes:${NC}"
PROCESSES=$(ps aux | grep -E "uvicorn|next start" | grep -v grep)
if [ -z "$PROCESSES" ]; then
    echo -e "${RED}✗ No services running${NC}"
else
    echo "$PROCESSES"
fi
echo ""

# Check ports
echo -e "${YELLOW}🔌 Port Status:${NC}"
for port in 8000 8001 5001; do
    if lsof -i:$port > /dev/null 2>&1; then
        PID=$(lsof -ti:$port)
        echo -e "${GREEN}✓ Port $port: IN USE (PID: $PID)${NC}"
    else
        echo -e "${RED}✗ Port $port: FREE${NC}"
    fi
done
echo ""

# Check service health
echo -e "${YELLOW}🏥 Service Health:${NC}"

# Backend API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health)
    echo -e "${GREEN}✓ Backend API (8000): $HEALTH${NC}"
else
    echo -e "${RED}✗ Backend API (8000): NOT RESPONDING${NC}"
fi

# Scheduler
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8001/health)
    echo -e "${GREEN}✓ Scheduler (8001): $HEALTH${NC}"
else
    echo -e "${RED}✗ Scheduler (8001): NOT RESPONDING${NC}"
fi

# Frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 | grep -q "200"; then
    echo -e "${GREEN}✓ Frontend (5001): RUNNING${NC}"
else
    echo -e "${RED}✗ Frontend (5001): NOT RESPONDING${NC}"
fi
echo ""

# Check logs
echo -e "${YELLOW}📋 Recent Logs (last 5 lines):${NC}"
if [ -f logs/backend.log ]; then
    echo -e "${BLUE}Backend:${NC}"
    tail -n 5 logs/backend.log
    echo ""
fi

if [ -f logs/frontend.log ]; then
    echo -e "${BLUE}Frontend:${NC}"
    tail -n 5 logs/frontend.log
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}💡 Useful Commands:${NC}"
echo "  View logs:     tail -f logs/backend.log"
echo "  Restart:       ./restart-production.sh"
echo "  Stop:          ./stop-production.sh"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
