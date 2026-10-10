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

# Minimum Python required by pinned dependencies (requests>=2.33, urllib3>=2.8)
MIN_PY="3.10"

function py_ok() {
    "$1" -c "import sys; sys.exit(0 if sys.version_info >= tuple(map(int, '$MIN_PY'.split('.'))) else 1)" 2>/dev/null
}

# 1. Pick a Python interpreter (override with PYTHON=/path/to/python)
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
    for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1 && py_ok "$candidate"; then
            PYTHON="$candidate"
            break
        fi
    done
fi
if [[ -z "$PYTHON" ]] || ! py_ok "$PYTHON"; then
    echo -e "${RED}Python >= $MIN_PY is required. Install it or set PYTHON=/path/to/python.${NC}"
    exit 1
fi

# 2. Rebuild venv if it uses a Python older than the minimum
if [[ -d "$VENV_DIR" ]] && ! py_ok "$VENV_DIR/bin/python"; then
    echo -e "${YELLOW}Existing test venv uses Python < $MIN_PY; rebuilding...${NC}"
    rm -rf "$VENV_DIR"
fi

# 3. Ensure venv exists
if [[ ! -d "$VENV_DIR" ]]; then
    echo -e "${YELLOW}Creating test virtual environment with $("$PYTHON" --version)...${NC}"
    "$PYTHON" -m venv "$VENV_DIR"
fi

# 4. Activate venv
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# 5. Install main and test dependencies
pip install --upgrade pip
pip install -r "$MAIN_REQ"
pip install -r "$REQ_FILE"

# 6. Run the test suite
cd tests
./run_tests.sh
cd ..

deactivate

echo -e "${GREEN}All tests completed.${NC}" 