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

# Configuration
DOCKER_USER="pwhite00"
IMAGE_NAME="read_me_later"

# Check if we can access Docker Hub
echo -e "${YELLOW}Checking Docker Hub access...${NC}"
if ! docker pull hello-world:latest >/dev/null 2>&1; then
    echo -e "${RED}Error: Cannot access Docker Hub${NC}"
    echo -e "${YELLOW}Please ensure you have internet access and Docker is running${NC}"
    exit 1
fi

# Pull the latest image from Docker Hub
echo -e "${YELLOW}Pulling latest image from Docker Hub...${NC}"
if docker pull $DOCKER_USER/$IMAGE_NAME:latest >/dev/null 2>&1; then
    echo -e "${GREEN}Successfully pulled latest image from Docker Hub${NC}"
    DOCKER_IMAGE="$DOCKER_USER/$IMAGE_NAME:latest"
else
    echo -e "${YELLOW}Latest image not found on Docker Hub, checking for local build...${NC}"
    # Fallback to local image if Docker Hub image doesn't exist
    LATEST_IMAGE=$(docker images read_me_later --format "table {{.Tag}}" | grep -v TAG | sort -V | tail -1)
    if [[ -z "$LATEST_IMAGE" ]]; then
        echo -e "${YELLOW}No local image found, building locally...${NC}"
        ./build_image.sh
        LATEST_IMAGE=$(docker images read_me_later --format "table {{.Tag}}" | grep -v TAG | sort -V | tail -1)
    fi
    DOCKER_IMAGE="read_me_later:$LATEST_IMAGE"
fi

# Create the global script
SCRIPT_CONTENT="#!/bin/bash

# Read Me Later - Global command
# Usage: readlater \"Your message here\"

# Check if message is provided
if [[ \$# -eq 0 ]]; then
    echo \"Usage: readlater \\\"Your message here\\\"\"
    echo \"Example: readlater \\\"Check out this article: https://example.com\\\"\"
    echo \"\"
    echo \"Make sure you have created ~/.read_me_later.json with your webhook URL\"
    exit 1
fi

# Check if default config file exists
DEFAULT_CONFIG=\"\$HOME/.read_me_later.json\"

if [[ -f \"\$DEFAULT_CONFIG\" ]]; then
    # Use the default config file (silent mode)
    docker run --rm -v \"\$DEFAULT_CONFIG:/app/.read_me_later.json\" \\
        $DOCKER_IMAGE \\
        --message \"\$*\" 2>/dev/null
    
    if [[ \$? -eq 0 ]]; then
        echo \"✅ Message sent to Slack for later reading\"
    else
        echo \"❌ Failed to send message\"
        exit 1
    fi
else
    echo \"Error: Configuration file not found: \$DEFAULT_CONFIG\"
    echo \"\"
    echo \"Please create it with your Slack webhook URL:\"
    echo \"cp .read_me_later.example.json ~/.read_me_later.json\"
    echo \"nano ~/.read_me_later.json\"
    exit 1
fi"

# Determine installation location - use user's home directory
INSTALL_DIR="$HOME/bin"

# Create the bin directory if it doesn't exist
if [[ ! -d "$INSTALL_DIR" ]]; then
    echo -e "${YELLOW}Creating $INSTALL_DIR directory...${NC}"
    mkdir -p "$INSTALL_DIR"
fi

# Install the script
echo "$SCRIPT_CONTENT" > "$INSTALL_DIR/readlater"
chmod +x "$INSTALL_DIR/readlater"

# Check if $HOME/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}Adding $INSTALL_DIR to PATH...${NC}"
    echo ""
    echo -e "${GREEN}Please add the following line to your shell profile (.bashrc, .zshrc, etc.):${NC}"
    echo -e "${YELLOW}export PATH=\"\$HOME/bin:\$PATH\"${NC}"
    echo ""
    echo -e "${GREEN}Or run this command to add it now:${NC}"
    echo -e "${YELLOW}echo 'export PATH=\"\$HOME/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc${NC}"
    echo ""
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
echo -e "${GREEN}Image used:${NC}"
echo "  $DOCKER_IMAGE"
echo ""
echo -e "${GREEN}To uninstall:${NC}"
echo "  rm $INSTALL_DIR/readlater" 