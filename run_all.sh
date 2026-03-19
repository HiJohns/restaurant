#!/bin/bash

# Exit on error
set -e

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Restaurant Project - Dev Environment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo "  Stopping backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "  Stopping frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}All processes stopped.${NC}"
    exit 0
}

# Set trap to catch Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created.${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    echo ""
else
    echo -e "${YELLOW}No requirements.txt found. Assuming dependencies are installed.${NC}"
    echo ""
fi

# Start FastAPI backend in the background
echo -e "${BLUE}Starting FastAPI backend on http://localhost:8000...${NC}"
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
echo ""

# Wait a moment for backend to start
sleep 3

# Go to frontend and start npm dev server
echo -e "${BLUE}Starting React frontend on http://localhost:5174...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Backend running at:  http://localhost:8000${NC}"
echo -e "${GREEN}✓ Frontend running at: http://localhost:5174${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
