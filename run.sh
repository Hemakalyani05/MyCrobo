#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "🛡️  Starting CodeSentinel AI (Backend & UI on port 8000)  "
echo "=========================================================="

if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/venv
    backend/venv/bin/pip install -r backend/requirements.txt
fi

if [ ! -d "frontend/dist" ]; then
    echo "Building frontend static assets..."
    cd frontend && npm install && npm run build && cd ..
fi

echo "🚀 CodeSentinel AI is launching at: http://localhost:8000"
PYTHONPATH=backend backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
