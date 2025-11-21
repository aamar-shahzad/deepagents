#!/bin/bash

# Deep Agents Builder - Startup Script

echo "🧠🤖 Deep Agents Builder"
echo "======================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Change to the script directory
cd "$(dirname "$0")"

# Install backend dependencies if not already installed
echo "📦 Checking backend dependencies..."
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/venv
    source backend/venv/bin/activate
    echo "Installing dependencies..."
    pip install -q -r backend/requirements.txt
    pip install -q ../../
else
    source backend/venv/bin/activate
fi

# Check if backend port is already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend might already be running."
    echo "   If not, please stop the process using port 8000 and try again."
else
    # Start backend
    echo "🚀 Starting backend server on http://localhost:8000"
    cd backend
    python main.py &
    BACKEND_PID=$!
    cd ..
    sleep 2
fi

# Check if frontend port is in use
if check_port 8080; then
    echo "⚠️  Port 8080 is already in use. Frontend might already be running."
else
    # Start frontend
    echo "🚀 Starting frontend server on http://localhost:8080"
    cd frontend
    python3 -m http.server 8080 &
    FRONTEND_PID=$!
    cd ..
    sleep 1
fi

echo ""
echo "✅ Deep Agents Builder is running!"
echo ""
echo "   Frontend: http://localhost:8080"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    # Kill any remaining python processes on these ports
    pkill -f "main.py" 2>/dev/null
    pkill -f "http.server 8080" 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM

# Wait for interrupt
wait
