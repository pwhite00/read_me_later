# Changelog

All notable changes to the Read Me Later project will be documented in this file.

## [1.2.0] - 2025-01-13

### Added
- **Enhanced Security Features**:
  - **Webhook URL Validation**: Validates that webhook URLs match Slack's expected format
  - **Message Length Limits**: Enforces 3000 character limit (Slack's maximum)
  - **Rate Limiting**: File-based rate limiting (10 requests per 60 seconds)
  - **Request Timeouts**: 10-second timeout for HTTP requests
  - **User-Agent Headers**: Proper identification in requests
- **Comprehensive Testing**: 
  - 36 test cases with 99% code coverage
  - Security feature testing
  - Edge case validation
  - Integration testing
- **Error Codes**: Specific error codes for different failure scenarios
  - Code 4: Message too long
  - Code 5: Rate limited
  - Code 6: Invalid webhook URL

### Changed
- **Version**: Updated to 1.2.0
- **Error Handling**: More specific error messages and return codes
- **Security**: Fail-open rate limiting (allows requests if rate limiting fails)

### Security
- **Input Validation**: All user inputs are validated before processing
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Webhook Security**: Ensures only legitimate Slack webhooks are accepted
- **Request Security**: Timeouts and proper headers for all HTTP requests

## [1.1.0] - 2025-01-13

### Added
- **Docker Support**: Complete Docker containerization with security improvements
- **Multiple Usage Options**: 
  - Global installation script (`./install.sh`)
  - Local wrapper script (`./readlater.sh`)
  - Environment variable wrapper (`./readlater-env.sh`)
  - Direct Docker usage
- **Default Configuration**: Automatic loading from `~/.read_me_later.json`
- **Multi-Architecture Support**: Builds for AMD64, ARM64, and ARMv7
- **Comprehensive Documentation**: Updated README with examples and best practices

### Changed
- **Dependencies Updated**: All Python packages updated to latest versions (2025)
  - `certifi`: 2023.7.22 → 2025.7.9
  - `charset-normalizer`: 3.2.0 → 3.4.2
  - `idna`: 3.4 → 3.10
  - `requests`: 2.31.0 → 2.32.4
  - `urllib3`: 2.0.4 → 2.5.0
- **Security Improvements**: 
  - Docker container runs as non-root user
  - Smaller base image (python:3.11-slim)
  - Updated dependencies with security patches
- **Better Error Handling**: Improved error messages and user feedback
- **Code Quality**: Fixed hardcoded webhook placeholder

### Fixed
- **Hardcoded Webhook**: Removed placeholder that would cause errors
- **Build Process**: Improved build script with better error handling
- **Documentation**: Updated all examples and instructions

### Security
- **Non-root Container**: Docker image runs as `appuser` instead of root
- **Dependency Security**: All packages updated to latest secure versions
- **Configuration Security**: Webhook URLs kept out of Docker images

## [1.0.0] - 2024-01-13

### Added
- Initial Python script for posting messages to Slack
- Basic command-line interface
- Support for webhook configuration via command line and JSON files
- Basic error handling and validation

### Dependencies
- `certifi==2023.7.22`
- `charset-normalizer==3.2.0`
- `idna==3.4`
- `requests==2.31.0`
- `urllib3==2.0.4` 