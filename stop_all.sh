#!/bin/bash
# Quick stop script for restaurant project

echo "Stopping restaurant project servers..."

# Kill uvicorn backend
pkill -f "uvicorn main:app" 2>/dev/null

# Kill npm frontend  
pkill -f "npm run dev" 2>/dev/null

echo "All servers stopped."
