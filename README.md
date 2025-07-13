# Read Me Later

A Python tool for sending messages to a Slack channel via webhooks. Perfect for saving articles, links, or notes to read later.

[![Docker Hub](https://img.shields.io/docker/pulls/pwhite00/read_me_later.svg)](https://hub.docker.com/r/pwhite00/read_me_later)
[![Docker Image Size](https://img.shields.io/docker/image-size/pwhite00/read_me_later/latest)](https://hub.docker.com/r/pwhite00/read_me_later)

**🐳 Docker Hub**: [pwhite00/read_me_later](https://hub.docker.com/r/pwhite00/read_me_later)

## Features

- 🐳 **Docker Support**: Run anywhere with Docker
- 🔧 **Flexible Configuration**: Multiple ways to configure Slack webhooks
- 🛡️ **Secure**: Runs as non-root user in Docker
- 📦 **Lightweight**: Small Docker image size
- 🔄 **Multi-Architecture**: Supports AMD64, ARM64, and ARMv7

## Quick Reference

### One-Liner Usage
```bash
# Global installation (recommended)
./install.sh && readlater "Your message here"

# Local wrapper
./readlater.sh "Your message here"

# Direct Docker (from Docker Hub)
docker run --rm -v ~/.read_me_later.json:/app/.read_me_later.json pwhite00/read_me_later:latest --message "Your message here"
```

## Quick Start with Docker

### Option 1: Use Docker Hub (Recommended)

```bash
# Pull and run directly from Docker Hub
docker run --rm pwhite00/read_me_later:latest \
  --webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --message "Check out this article: https://example.com"

# Using a credentials file
echo '{"webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"}' > slack_creds.json
docker run --rm -v $(pwd)/slack_creds.json:/app/creds.json pwhite00/read_me_later:latest \
  --creds-file /app/creds.json \
  --message "Another interesting link: https://example.org"
```

### Option 2: Build Locally (for development)

```bash
# Build for your current architecture
./build_image.sh

# Or build and publish to Docker Hub
./build_image.sh publish
```

**Note**: The build script creates timestamped tags (e.g., `read_me_later:20250713081336`). For production use, prefer the Docker Hub image `pwhite00/read_me_later:latest`.

## Installation Options

### Option 1: Docker (Recommended)

The easiest way to use this tool is with Docker:

```bash
# Pull from Docker Hub (recommended)
docker pull pwhite00/read_me_later:latest

# Or build locally (for development)
./build_image.sh
```

### Option 2: Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python read_me_later.py --webhook "YOUR_WEBHOOK_URL" --message "Your message"
```

## Configuration

### Slack Webhook Setup

1. Go to your Slack workspace
2. Create a new app or use an existing one
3. Enable "Incoming Webhooks"
4. Create a webhook for your desired channel
5. Copy the webhook URL

### Webhook Configuration Methods

#### Method 1: Command Line (Recommended for Docker)
```bash
docker run --rm pwhite00/read_me_later:latest \
  --webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --message "Your message here"
```

#### Method 2: JSON Configuration File
Create a file `slack_creds.json`:
```json
{
  "webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

Then use:
```bash
docker run --rm -v $(pwd)/slack_creds.json:/app/creds.json pwhite00/read_me_later:latest \
  --creds-file /app/creds.json \
  --message "Your message here"
```

#### Method 3: Default Configuration File (Recommended)
Create `~/.read_me_later.json` in your home directory:
```json
{
  "webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

Then simply run:
```bash
docker run --rm -v ~/.read_me_later.json:/app/.read_me_later.json pwhite00/read_me_later:latest \
  --message "Your message here"
```

**Note**: The script will automatically look for `~/.read_me_later.json` if no webhook is provided via command line arguments.

## Usage Examples

### Save an Article Link
```bash
docker run --rm pwhite00/read_me_later:latest \
  --webhook "YOUR_WEBHOOK_URL" \
  --message "📚 Article to read later: https://medium.com/interesting-article"
```

### Save a Note
```bash
docker run --rm pwhite00/read_me_later:latest \
  --webhook "YOUR_WEBHOOK_URL" \
  --message "💡 Remember to check the new API documentation"
```

### Create an Alias (Optional)
Add to your shell profile (`.bashrc`, `.zshrc`, etc.):
```bash
alias readlater='docker run --rm -v ~/.read_me_later.json:/app/.read_me_later.json pwhite00/read_me_later:latest --message'
```

Then use:
```bash
readlater "Check out this cool project: https://github.com/example/project"
```

### Quick Setup Options

#### Option 1: Global Installation (Recommended)
```bash
# Install globally (requires sudo)
./install.sh

# Then use from anywhere:
readlater "Your message here"
```

#### Option 2: Local Wrapper Script
1. Copy the example configuration:
```bash
cp .read_me_later.example.json ~/.read_me_later.json
```

2. Edit the file with your webhook URL:
```bash
nano ~/.read_me_later.json
```

3. Use the wrapper script:
```bash
./readlater.sh "Your message here"
```

#### Option 3: Environment Variable
```bash
# Set webhook once
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Use anytime
./readlater-env.sh "Your message here"
```

#### Option 4: Direct Docker (for advanced users)
```bash
docker run --rm -v ~/.read_me_later.json:/app/.read_me_later.json \
  pwhite00/read_me_later:latest --message "Your message here"
```

## Development

### Building for Different Architectures

```bash
# Build for current architecture
./build_image.sh

# Build and publish for current architecture
./build_image.sh publish

# Build and publish for all supported architectures
./build_image.sh publish-all
```

### Local Development

```bash
# Set up development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python read_me_later.py --help
```

## Testing

See [TESTING.md](./TESTING.md) for the full testing guide, including:
- How to run all tests with `./test.sh`
- Python coverage reporting
- Shell script linting
- Docker and integration checks
- How to add or edit tests

A summary of test results and coverage will be shown in your terminal after running the test suite.

## Requirements

### Python Dependencies
```
certifi==2025.7.9
charset-normalizer==3.4.2
idna==3.10
requests==2.32.4
urllib3==2.5.0
```

### System Requirements
- Python 3.7+ (for local development)
- Docker (for containerized usage)
- Slack workspace with webhook access

## Security Features

### Input Validation
- **Webhook URL Validation**: Ensures only legitimate Slack webhook URLs are accepted
- **Message Length Limits**: Enforces 3000 character limit (Slack's maximum)
- **Input Sanitization**: Validates all user inputs before processing

### Rate Limiting
- **Request Limits**: 10 requests per 60-second window
- **File-based Storage**: Rate limit data stored in `~/.read_me_later_rate_limit`
- **Fail-open Design**: If rate limiting fails, requests are allowed (graceful degradation)

### Network Security
- **Request Timeouts**: 10-second timeout for all HTTP requests
- **User-Agent Headers**: Proper identification in requests
- **HTTPS Enforcement**: Only accepts HTTPS webhook URLs

### Container Security
- **Non-root User**: Docker container runs as `appuser` instead of root
- **Minimal Base Image**: Uses `python:3.11-slim` for smaller attack surface
- **Secure Dependencies**: All packages updated to latest secure versions

### Configuration Security
- **Webhook Protection**: Webhook URLs kept out of Docker images
- **File Permissions**: Configuration files use appropriate permissions
- **Environment Variables**: Support for secure credential management

### Error Handling
- **Specific Error Codes**: 
  - Code 4: Message too long
  - Code 5: Rate limited  
  - Code 6: Invalid webhook URL
- **Graceful Failures**: Clear error messages without exposing sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker and local Python
5. Submit a pull request

## Version History

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and improvements.

### Current Version: 1.2.0
- **Enhanced Security**: Webhook validation, rate limiting, and message length limits
- **Comprehensive Testing**: 36 tests with 99% code coverage
- **Docker Support**: Complete containerization with security improvements
- **Multiple Usage Options**: Global installation, wrapper scripts, and direct Docker usage
- **Updated Dependencies**: All packages updated to latest versions (2025)
- **Security**: Non-root container, input validation, and rate limiting

## License

This project is open source. Feel free to use and modify as needed.
