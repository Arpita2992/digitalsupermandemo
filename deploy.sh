#!/bin/bash
# Production Deployment Script for Digital Superman

set -e

echo "🚀 Starting Digital Superman Production Deployment..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one based on .env.example"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads output logs

# Set proper permissions
echo "🔒 Setting permissions..."
chmod 755 uploads output logs
chmod 600 .env

# Run production checks
echo "🔍 Running production checks..."
python -c "
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Check required environment variables
required_vars = [
    'AZURE_AI_AGENT1_ENDPOINT',
    'AZURE_AI_AGENT1_KEY',
    'AZURE_AI_AGENT2_ENDPOINT',
    'AZURE_AI_AGENT2_KEY',
    'AZURE_AI_AGENT3_ENDPOINT',
    'AZURE_AI_AGENT3_KEY',
    'AZURE_AI_AGENT4_ENDPOINT',
    'AZURE_AI_AGENT4_KEY',
    'SECRET_KEY'
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f'❌ Missing required environment variables: {missing_vars}')
    sys.exit(1)

print('✅ All required environment variables are set')
"

# Test application startup
echo "🧪 Testing application startup..."
timeout 10 python app.py > /dev/null 2>&1 &
PID=$!
sleep 5

if kill -0 $PID 2>/dev/null; then
    echo "✅ Application starts successfully"
    kill $PID
else
    echo "❌ Application failed to start"
    exit 1
fi

echo "✅ Production deployment completed successfully!"
echo "🚀 To start the application:"
echo "   - For development: python app.py"
echo "   - For production: gunicorn -w 4 -b 0.0.0.0:8000 app:app"
