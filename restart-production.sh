#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping services...${NC}"
pkill -f uvicorn || true
pkill -f "next start" || true
sleep 3

echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
cd /opt/ai-llmstxt-generator
git pull origin feature/self-hosted-deployment

echo -e "${YELLOW}📦 Installing dependencies...${NC}"
npm install

echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

echo -e "${YELLOW}🔨 Building frontend...${NC}"
npm run build

echo -e "${YELLOW}📁 Creating logs directory...${NC}"
mkdir -p logs

echo -e "${GREEN}🚀 Starting backend API...${NC}"
cd backend
source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}   Backend PID: $BACKEND_PID${NC}"
cd ..

echo -e "${GREEN}🚀 Starting scheduler...${NC}"
cd backend
source venv/bin/activate
nohup python3 -m uvicorn scheduler:app --host 0.0.0.0 --port 8001 > ../logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo -e "${GREEN}   Scheduler PID: $SCHEDULER_PID${NC}"
cd ..

echo -e "${GREEN}🚀 Starting frontend...${NC}"
NODE_ENV=production nohup npm run start -- --port 5001 > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}   Frontend PID: $FRONTEND_PID${NC}"

echo ""
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo ""
echo -e "${YELLOW}📊 Service Status:${NC}"
echo "  Backend API:  http://localhost:8000"
echo "  Scheduler:    http://localhost:8001"
echo "  Frontend:     http://localhost:5001"
echo ""
echo -e "${YELLOW}🔍 Check Status:${NC}"
echo "  curl http://localhost:8000/health"
echo "  curl -I http://localhost:5001"
echo ""
echo -e "${YELLOW}📋 View Logs:${NC}"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo "  tail -f logs/scheduler.log"
echo ""
echo -e "${YELLOW}🔍 Check Running Processes:${NC}"
echo "  ps aux | grep -E 'uvicorn|next start' | grep -v grep"
echo ""
echo -e "${YELLOW}🛑 Stop All Services:${NC}"
echo "  pkill -f uvicorn && pkill -f 'next start'"
echo ""
