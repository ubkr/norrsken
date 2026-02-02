#!/bin/bash
# Start the Aurora Visibility frontend server

cd "$(dirname "$0")/frontend"

echo "Starting Aurora Visibility Frontend..."
echo "Frontend will be available at http://localhost:3000"
echo ""

python3 -m http.server 3000
