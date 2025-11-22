#!/bin/bash
# Setup script for Dollar AI Voice Assistant

set -e

echo "🚀 Setting up Dollar AI Voice Assistant..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install system dependencies (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
    if ! command -v brew &> /dev/null; then
        echo "⚠️  Homebrew not found. Install it from https://brew.sh/"
    else
        if ! brew list portaudio &> /dev/null; then
            echo "📦 Installing portaudio..."
            brew install portaudio
        fi
    fi
fi

# Install system dependencies (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    if command -v apt-get &> /dev/null; then
        echo "📦 Installing system dependencies..."
        sudo apt-get update
        sudo apt-get install -y portaudio19-dev python3-pyaudio
    elif command -v yum &> /dev/null; then
        echo "📦 Installing system dependencies..."
        sudo yum install -y portaudio-devel python3-pyaudio
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Get a Picovoice access key from https://console.picovoice.ai/ (optional but recommended)"
echo "2. Add it to agent/config.yaml"
echo "3. Run: cd agent && python main.py"
echo ""

