#!/bin/bash

# Script to restart backend server with fixed code
set -e

cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend

echo "🔴 Stopping old uvicorn processes..."
pkill -f "uvicorn src.main:app" || true
sleep 2

echo "🟢 Starting fresh backend server..."
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
