#!/bin/bash

# YojnaMitra AI - EC2 Deployment Script
# Usage: Run this script on your EC2 instance

echo "🚀 Starting YojnaMitra AI Deployment..."
echo "=========================================="

# Navigate to app directory
cd yojnamitra-ai || { echo "❌ Error: yojnamitra-ai directory not found"; exit 1; }

# Fetch latest code
echo "📥 Fetching latest code from GitHub..."
git fetch origin

# Reset to match GitHub
echo "🔄 Resetting to latest version..."
git reset --hard origin/main

# Kill old process
echo "🛑 Stopping old Streamlit process..."
pkill -f streamlit

# Wait a moment
sleep 2

# Start new process
echo "▶️  Starting Streamlit app..."
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &

# Wait for startup
sleep 5

# Check if running
if ps aux | grep -v grep | grep streamlit > /dev/null; then
    echo "✅ Deployment successful!"
    echo "=========================================="
    echo "🌐 Your app is live at: http://13.201.55.10:8501"
    echo ""
    echo "📊 View logs: tail -f streamlit.log"
    echo "🔍 Check status: ps aux | grep streamlit"
else
    echo "❌ Deployment failed!"
    echo "Check logs: tail -50 streamlit.log"
    exit 1
fi
