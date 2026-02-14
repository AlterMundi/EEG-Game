#!/bin/bash
# Neurofeedback Game - Start Script
# Starts the WebSocket server and web app

echo "============================================================"
echo "   Neurofeedback Focus Game - Startup"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import websockets, scipy, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Missing dependencies. Run: pip install -r requirements.txt"
    exit 1
fi

echo "✓ All dependencies installed"
echo ""

# Kill any existing instances
echo "Checking for existing servers..."
pkill -f "python.*websocket_server.py" 2>/dev/null
pkill -f "python.*osc_simulator.py" 2>/dev/null
sleep 1

echo "Starting WebSocket Server..."
python3 websocket_server.py &
WS_PID=$!
sleep 2

# Check if WebSocket server started successfully
if ! ps -p $WS_PID > /dev/null; then
    echo "❌ Error: WebSocket server failed to start"
    exit 1
fi

echo "✓ WebSocket server running (PID: $WS_PID)"
echo ""

# Display connection info
echo "============================================================"
echo "   Server Ready!"
echo "============================================================"
echo ""
echo "WebSocket Server: ws://localhost:8765"
echo "OSC Listening:    UDP port 5000"
echo ""
echo "To start the web app, open a new terminal and run:"
echo "  cd webapp"
echo "  python3 -m http.server 8000"
echo ""
echo "Then open: http://localhost:8000"
echo ""
echo "Configure Mind Monitor to stream to:"
echo "  IP:   $(hostname -I | awk '{print $1}')"
echo "  Port: 5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Wait for WebSocket server
wait $WS_PID
