# Changelog

All notable changes to the Read Me Later project will be documented in this file.

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