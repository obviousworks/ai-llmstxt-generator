#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping all services...${NC}"

# Show running processes before stopping
echo -e "${YELLOW}Current processes:${NC}"
ps aux | grep -E "uvicorn|next start" | grep -v grep || echo "No processes found"
echo ""

# Kill processes
pkill -f uvicorn && echo -e "${GREEN}✓ Stopped uvicorn processes${NC}" || echo -e "${RED}✗ No uvicorn processes found${NC}"
pkill -f "next start" && echo -e "${GREEN}✓ Stopped Next.js processes${NC}" || echo -e "${RED}✗ No Next.js processes found${NC}"

sleep 2

# Verify ports are free
echo ""
echo -e "${YELLOW}Checking ports...${NC}"
if lsof -i:8000 > /dev/null 2>&1; then
    echo -e "${RED}✗ Port 8000 still in use${NC}"
else
    echo -e "${GREEN}✓ Port 8000 is free${NC}"
fi

if lsof -i:8001 > /dev/null 2>&1; then
    echo -e "${RED}✗ Port 8001 still in use${NC}"
else
    echo -e "${GREEN}✓ Port 8001 is free${NC}"
fi

if lsof -i:5001 > /dev/null 2>&1; then
    echo -e "${RED}✗ Port 5001 still in use${NC}"
else
    echo -e "${GREEN}✓ Port 5001 is free${NC}"
fi

echo ""
echo -e "${GREEN}✅ All services stopped!${NC}"
