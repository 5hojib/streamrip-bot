#!/bin/bash

# Streamrip Bot Startup Script

echo "🎵 Starting Streamrip Bot..."

# Check if Python 3.9+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required (found $python_version)"
    exit 1
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo "❌ config.py not found"
    echo "📋 Please copy config_sample.py to config.py and configure it"
    echo "   cp config_sample.py config.py"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create downloads directory
mkdir -p downloads

# Set permissions
chmod +x bot.py

# Start the bot
echo "🚀 Starting bot..."
python3 bot.py
