#!/bin/bash
# Wrapper to run all tests in the tests/ directory
set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

VENV_DIR=".venv-test"
REQ_FILE="tests/requirements-test.txt"
MAIN_REQ="requirements.txt"

# 1. Ensure venv exists
if [[ ! -d "$VENV_DIR" ]]; then
    echo -e "${YELLOW}Creating test virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate venv
source "$VENV_DIR/bin/activate"

# 3. Install main and test dependencies
pip install --upgrade pip
pip install -r "$MAIN_REQ"
pip install -r "$REQ_FILE"

# 4. Run the test suite
cd tests
./run_tests.sh
cd ..

deactivate

echo -e "${GREEN}All tests completed.${NC}" 