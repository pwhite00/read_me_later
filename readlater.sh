#!/bin/bash

# Read Me Later - Convenient wrapper script
# Usage: ./readlater.sh "Your message here"

# Check if message is provided
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"Your message here\""
    echo "Example: $0 \"Check out this article: https://example.com\""
    echo ""
    echo "Make sure you have created ~/.read_me_later.json with your webhook URL"
    exit 1
fi

# Check if default config file exists
DEFAULT_CONFIG="$HOME/.read_me_later.json"

if [[ -f "$DEFAULT_CONFIG" ]]; then
    # Find the latest built image
    LATEST_IMAGE=$(docker images read_me_later --format "table {{.Tag}}" | grep -v TAG | sort -V | tail -1)
    
    if [[ -z "$LATEST_IMAGE" ]]; then
        echo "Error: No read_me_later Docker image found"
        echo "Please run: ./build_image.sh"
        exit 1
    fi
    
    # Use the default config file (silent mode)
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
fi 