#!/bin/bash

# Install script for Read Me Later
# This script installs the readlater command globally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing Read Me Later...${NC}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH${NC}"
    exit 1
fi

# Build the Docker image if it doesn't exist
LATEST_IMAGE=$(docker images read_me_later --format "table {{.Tag}}" | grep -v TAG | sort -V | tail -1)
if [[ -z "$LATEST_IMAGE" ]]; then
    echo -e "${YELLOW}Building Docker image...${NC}"
    ./build_image.sh
    LATEST_IMAGE=$(docker images read_me_later --format "table {{.Tag}}" | grep -v TAG | sort -V | tail -1)
fi

# Create the global script
SCRIPT_CONTENT='#!/bin/bash

# Read Me Later - Global command
# Usage: readlater "Your message here"

# Check if message is provided
if [[ $# -eq 0 ]]; then
    echo "Usage: readlater \"Your message here\""
    echo "Example: readlater \"Check out this article: https://example.com\""
    echo ""
    echo "Make sure you have created ~/.read_me_later.json with your webhook URL"
    exit 1
fi

# Check if default config file exists
DEFAULT_CONFIG="$HOME/.read_me_later.json"

if [[ -f "$DEFAULT_CONFIG" ]]; then
    # Use the default config file (silent mode)
    # Find the latest built image
    LATEST_IMAGE=$(docker images read_me_later --format "table {{.Tag}}" | grep -v TAG | sort -V | tail -1)
    
    docker run --rm -v "$DEFAULT_CONFIG:/app/.read_me_later.json" \
        read_me_later:$LATEST_IMAGE \
        --message "$*" 2>/dev/null
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Message sent to Slack for later reading"
    else
        echo "❌ Failed to send message"
        exit 1
    fi
else
    echo "Error: Configuration file not found: $DEFAULT_CONFIG"
    echo ""
    echo "Please create it with your Slack webhook URL:"
    echo "cp .read_me_later.example.json ~/.read_me_later.json"
    echo "nano ~/.read_me_later.json"
    exit 1
fi'

# Determine installation location
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    INSTALL_DIR="/usr/local/bin"
else
    # Linux
    INSTALL_DIR="/usr/local/bin"
fi

# Check if we can write to the install directory
if [[ ! -w "$INSTALL_DIR" ]]; then
    echo -e "${YELLOW}Need sudo permissions to install to $INSTALL_DIR${NC}"
    sudo mkdir -p "$INSTALL_DIR"
    echo "$SCRIPT_CONTENT" | sudo tee "$INSTALL_DIR/readlater" > /dev/null
    sudo chmod +x "$INSTALL_DIR/readlater"
else
    echo "$SCRIPT_CONTENT" > "$INSTALL_DIR/readlater"
    chmod +x "$INSTALL_DIR/readlater"
fi

# Create example config if it doesn't exist
if [[ ! -f "$HOME/.read_me_later.json" ]]; then
    echo -e "${YELLOW}Creating example configuration file...${NC}"
    cp .read_me_later.example.json "$HOME/.read_me_later.json"
    echo -e "${GREEN}Created $HOME/.read_me_later.json${NC}"
    echo -e "${YELLOW}Please edit this file with your Slack webhook URL${NC}"
fi

echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo -e "${GREEN}Usage:${NC}"
echo "  readlater \"Your message here\""
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Edit ~/.read_me_later.json with your Slack webhook URL"
echo "  2. Test with: readlater \"Hello from Read Me Later!\""
echo ""
echo -e "${GREEN}To uninstall:${NC}"
echo "  sudo rm $INSTALL_DIR/readlater" 