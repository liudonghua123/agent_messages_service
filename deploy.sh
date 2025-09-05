#!/bin/bash
set -e

# Build frontend
cd frontend
npm run build
if [ $? -ne 0 ]; then
    echo "Frontend build failed!"
    exit 1
fi

# Copy files to backend/static
mkdir -p ../backend/static
cp -r dist/* ../backend/static/

echo "Deployment completed!"
echo "You can now run the backend server:"
echo "cd backend"
echo "python main.py"
