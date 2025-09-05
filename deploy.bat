@echo off
echo Building frontend...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo Frontend build failed!
    pause
    exit /b 1
)

echo Copying files to backend/static...
if not exist "..\backend\static" mkdir "..\backend\static"
xcopy /E /I /Y "dist\*" "..\backend\static\"

echo Deployment completed!
echo You can now run the backend server:
echo cd backend
echo python main.py

pause