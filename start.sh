#!/bin/bash

echo "=================================="
echo "AWS FinOps Agent - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Installing manually..."
    echo ""
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required. Please install Python 3.9+ first."
        exit 1
    fi
    
    # Check Node
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required. Please install Node.js 18+ first."
        exit 1
    fi
    
    echo "✓ Python found: $(python3 --version)"
    echo "✓ Node found: $(node --version)"
    echo ""
    
    # Start backend
    echo "📦 Installing backend dependencies..."
    cd backend
    pip3 install -r requirements.txt
    
    echo ""
    echo "🚀 Starting backend server..."
    python3 server.py &
    BACKEND_PID=$!
    cd ..
    
    # Start dashboard
    echo ""
    echo "📦 Installing dashboard dependencies..."
    cd dashboard
    npm install
    
    echo ""
    echo "🚀 Starting dashboard..."
    npm start &
    DASHBOARD_PID=$!
    cd ..
    
    echo ""
    echo "✅ FinOps Agent is starting!"
    echo ""
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔧 API: http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop"
    
    # Wait for user interrupt
    trap "kill $BACKEND_PID $DASHBOARD_PID 2>/dev/null" EXIT
    wait
    
else
    echo "✓ Docker found"
    echo ""
    echo "🚀 Starting with Docker Compose..."
    docker-compose up -d
    
    echo ""
    echo "✅ FinOps Agent is running!"
    echo ""
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔧 API: http://localhost:8000"
    echo ""
    echo "To stop: docker-compose down"
    echo "To view logs: docker-compose logs -f"
fi
