#!/bin/bash

echo "🚀 Starting Hoeflon AI Portal System"
echo "===================================="

PROJECT_ROOT="/home/jfrank/projecten/hoeflon/hoeflon ai/hoeflon-ai-portaal"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if backend is already running
if curl -s http://localhost:8504/health > /dev/null; then
    echo -e "${GREEN}✅ Backend already running on port 8504${NC}"
else
    echo -e "${YELLOW}📦 Starting backend on port 8504...${NC}"
    cd backend
    # Start backend in background
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8504 --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    sleep 5
    
    if curl -s http://localhost:8504/health > /dev/null; then
        echo -e "${GREEN}✅ Backend started successfully${NC}"
    else
        echo -e "${RED}❌ Backend failed to start${NC}"
        cat ../logs/backend.log
        exit 1
    fi
    cd ..
fi

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ Frontend already running on port 3000${NC}"
else
    echo -e "${YELLOW}🎨 Frontend not running. Start with:${NC}"
    echo "cd react-frontend && npm install && npm start"
fi

echo ""
echo -e "${GREEN}🎉 System Status:${NC}"
echo "Backend: http://localhost:8504"
echo "Frontend: http://localhost:3000"
echo ""
echo "📋 Available endpoints:"
echo "  GET  /health        - System health check"
echo "  GET  /status        - Detailed system status"
echo "  POST /chat          - Main chat interface"
echo "  POST /company_chat  - Company knowledge queries"
echo "  GET  /documents/*   - Document processing"
echo "  GET  /memory/*      - Memory system"
echo ""
echo "🧪 To run tests: ./scripts/run_full_tests.sh"