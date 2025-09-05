@echo off
echo Starting Agent Messages Service in development mode...

echo Installing backend dependencies...
pip install -r requirements.txt

echo Starting backend server...
cd backend
start "Backend Server" python main.py

echo Waiting for backend to start...
timeout /t 3

echo Starting frontend development server...
cd ..\frontend
start "Frontend Dev Server" npm run dev

echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend Dev: http://localhost:5173
echo.
echo Press any key to stop all servers...
pause

echo Stopping servers...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul