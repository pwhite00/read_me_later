#!/bin/bash

# Read Me Later - Environment Variable Wrapper
# Usage: SLACK_WEBHOOK="your_webhook" ./readlater-env.sh "Your message here"
# Or: export SLACK_WEBHOOK="your_webhook" && ./readlater-env.sh "Your message here"

# Check if message is provided
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"Your message here\""
    echo "Example: $0 \"Check out this article: https://example.com\""
    echo ""
    echo "Set your webhook URL using one of these methods:"
    echo "  1. Environment variable: SLACK_WEBHOOK=\"your_webhook\" $0 \"message\""
    echo "  2. Export: export SLACK_WEBHOOK=\"your_webhook\" && $0 \"message\""
    echo "  3. Config file: Create ~/.read_me_later.json and use ./readlater.sh"
    exit 1
fi

# Check if webhook is provided via environment variable
if [[ -z "$SLACK_WEBHOOK" ]]; then
    echo "Error: SLACK_WEBHOOK environment variable not set"
    echo ""
    echo "Set it with:"
    echo "  export SLACK_WEBHOOK=\"https://hooks.slack.com/services/YOUR/WEBHOOK/URL\""
    echo ""
    echo "Or use the config file approach:"
    echo "  ./readlater.sh \"Your message here\""
    exit 1
fi

# Find the latest built image
LATEST_IMAGE=$(docker images read_me_later --format "table {{.Tag}}" | grep -v TAG | sort -V | tail -1)

if [[ -z "$LATEST_IMAGE" ]]; then
    echo "Error: No read_me_later Docker image found"
    echo "Please run: ./build_image.sh"
    exit 1
fi

# Run the Docker container with environment variable
docker run --rm -e SLACK_WEBHOOK="$SLACK_WEBHOOK" \
    read_me_later:$LATEST_IMAGE \
    --webhook "$SLACK_WEBHOOK" \
    --message "$*" 2>/dev/null

if [[ $? -eq 0 ]]; then
    echo "✅ Message sent to Slack for later reading"
else
    echo "❌ Failed to send message"
    exit 1
fi 