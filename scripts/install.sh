#!/bin/bash
# Quick install script for Aalap

set -e

echo "🎵 Installing Aalap..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required."
    echo "You have Python $PYTHON_VERSION"
    exit 1
fi

# Install using pip
echo "📦 Installing Aalap via pip..."
pip3 install git+https://github.com/caltycs/aalap.git

echo "✅ Aalap installed successfully!"
echo ""
echo "To get started:"
echo "  1. Set your API key: aalap config --api-key YOUR_KEY"
echo "  2. Launch Aalap: aalap"
echo ""
echo "For more information: https://github.com/caltycs/aalap"