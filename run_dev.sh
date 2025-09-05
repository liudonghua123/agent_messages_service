#!/bin/bash
set -e

echo "Starting Agent Messages Service in development mode..."

# Install backend dependencies
pip install -r requirements.txt

# Start backend server
cd backend
nohup python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend dev server
cd frontend
nohup npm run dev &
FRONTEND_PID=$!
cd ..

echo "Both servers are starting..."
echo "Backend: http://localhost:8000"
echo "Frontend Dev: http://localhost:5173"
echo
read -p "Press enter to stop all servers..."

# Stop servers
kill $BACKEND_PID $FRONTEND_PID
