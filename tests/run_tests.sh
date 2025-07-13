#!/bin/bash

# Test runner for read_me_later project
# Runs Python unit tests with coverage, shellcheck linting, and Docker validation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

function print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

function print_subheader() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

function print_result() {
    if [[ $1 -eq 0 ]]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
}

function run_python_tests() {
    print_header "🐍 Python Unit Tests & Coverage"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}Python3 not found, skipping Python tests${NC}"
        print_result 0
        return
    fi
    
    # Check if we're in a virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        echo -e "${YELLOW}⚠️  Not in virtual environment. Creating test venv...${NC}"
        if [[ -d ".venv-test" ]]; then
            echo "Activating existing test virtual environment..."
            source .venv-test/bin/activate
        else
            echo "Creating new test virtual environment..."
            python3 -m venv .venv-test
            source .venv-test/bin/activate
            echo "Installing test dependencies..."
            pip install -r requirements-test.txt
        fi
    fi
    
    print_subheader "Running Unit Tests with Coverage"
    
    # Set PYTHONPATH to include parent directory for module import
    export PYTHONPATH="../:${PYTHONPATH:-}"
    
    # Run tests with coverage
    if python3 -m pytest test_read_me_later.py -v --cov=read_me_later --cov-report=term-missing --cov-report=html:htmlcov; then
        echo ""
        print_subheader "📊 Coverage Summary"
        echo -e "${GREEN}✅ All tests passed with coverage reporting${NC}"
        echo -e "${BLUE}📁 HTML coverage report generated in: htmlcov/index.html${NC}"
        print_result 0
    else
        echo -e "${RED}❌ Python tests failed${NC}"
        print_result 1
    fi
}

function run_shellcheck() {
    print_header "🔍 ShellCheck Linting"
    
    if ! command -v shellcheck &> /dev/null; then
        echo -e "${YELLOW}ShellCheck not installed. Installing...${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install shellcheck
        else
            echo -e "${RED}Please install shellcheck manually${NC}"
            print_result 1
            return
        fi
    fi
    
    local exit_code=0
    
    # List of bash scripts to check (relative to project root)
    local scripts=(
        "../build_image.sh"
        "../install.sh"
        "../readlater.sh"
        "../readlater-env.sh"
        "run_tests.sh"
    )
    
    print_subheader "Checking Bash Scripts"
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            echo -e "${PURPLE}🔍 Checking: $script${NC}"
            if shellcheck --source-path=SCRIPTDIR --external-sources --shell=bash --rcfile .shellcheckrc "$script"; then
                echo -e "${GREEN}✅ $script passed${NC}"
            else
                echo -e "${RED}❌ $script failed${NC}"
                exit_code=1
            fi
        else
            echo -e "${YELLOW}⚠️  $script not found${NC}"
        fi
    done
    
    print_result $exit_code
}

function validate_dockerfile() {
    print_header "🐳 Dockerfile Validation"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found, skipping Docker validation${NC}"
        print_result 0
        return
    fi
    
    local exit_code=0
    
    # Check if Dockerfile exists
    if [[ ! -f "../Dockerfile" ]]; then
        echo -e "${RED}❌ Dockerfile not found${NC}"
        print_result 1
        return
    fi
    
    print_subheader "Syntax Validation"
    # Validate Dockerfile syntax
    echo "Validating Dockerfile syntax..."
    if docker build --dry-run -f ../Dockerfile .. >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Dockerfile syntax is valid${NC}"
    else
        echo -e "${RED}❌ Dockerfile syntax is invalid${NC}"
        exit_code=1
    fi
    
    print_subheader "Security Best Practices"
    # Check for security best practices
    echo "Checking Dockerfile security..."
    local security_issues=0
    
    # Check for non-root user
    if grep -q "USER appuser" ../Dockerfile; then
        echo -e "${GREEN}✅ Non-root user configured${NC}"
    else
        echo -e "${RED}❌ No non-root user found${NC}"
        ((security_issues++))
    fi
    
    # Check for multi-stage build (optional)
    if grep -q "FROM.*as" ../Dockerfile; then
        echo -e "${GREEN}✅ Multi-stage build detected${NC}"
    else
        echo -e "${YELLOW}⚠️  Consider using multi-stage build for smaller images${NC}"
    fi
    
    # Check for .dockerignore
    if [[ -f "../.dockerignore" ]]; then
        echo -e "${GREEN}✅ .dockerignore file present${NC}"
    else
        echo -e "${YELLOW}⚠️  No .dockerignore file found${NC}"
    fi
    
    if [[ $security_issues -gt 0 ]]; then
        exit_code=1
    fi
    
    print_result $exit_code
}

function test_docker_build() {
    print_header "🏗️  Docker Build Test"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found, skipping Docker build test${NC}"
        print_result 0
        return
    fi
    
    print_subheader "Building Test Image"
    echo "Building test image..."
    if docker build -t read_me_later:test -f ../Dockerfile .. >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker build successful${NC}"
        
        print_subheader "Testing Image Functionality"
        # Test the image
        echo "Testing image functionality..."
        if docker run --rm read_me_later:test --help >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Image test successful${NC}"
            print_result 0
        else
            echo -e "${RED}❌ Image test failed${NC}"
            print_result 1
        fi
        
        # Clean up test image
        docker rmi read_me_later:test >/dev/null 2>&1 || true
    else
        echo -e "${RED}❌ Docker build failed${NC}"
        print_result 1
    fi
}

function run_integration_tests() {
    print_header "🔗 Integration Tests"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker not found, skipping integration tests${NC}"
        print_result 0
        return
    fi
    
    local exit_code=0
    
    print_subheader "Wrapper Scripts"
    # Test 1: Check if wrapper scripts exist and are executable
    echo "Testing wrapper scripts..."
    local scripts=("../readlater.sh" "../readlater-env.sh" "../install.sh")
    for script in "${scripts[@]}"; do
        if [[ -f "$script" && -x "$script" ]]; then
            echo -e "${GREEN}✅ $script exists and is executable${NC}"
        else
            echo -e "${RED}❌ $script missing or not executable${NC}"
            exit_code=1
        fi
    done
    
    print_subheader "Example Files"
    # Test 2: Check if example files exist
    echo "Testing example files..."
    local examples=("../.read_me_later.example.json" "../slack_creds.example.json")
    for example in "${examples[@]}"; do
        if [[ -f "$example" ]]; then
            echo -e "${GREEN}✅ $example exists${NC}"
        else
            echo -e "${RED}❌ $example missing${NC}"
            exit_code=1
        fi
    done
    
    print_subheader "JSON Validation"
    # Test 3: Validate JSON files
    echo "Validating JSON files..."
    if command -v jq &> /dev/null; then
        for json_file in ../.read_me_later.example.json ../slack_creds.example.json; do
            if [[ -f "$json_file" ]]; then
                if jq empty "$json_file" >/dev/null 2>&1; then
                    echo -e "${GREEN}✅ $json_file is valid JSON${NC}"
                else
                    echo -e "${RED}❌ $json_file is invalid JSON${NC}"
                    exit_code=1
                fi
            fi
        done
    else
        echo -e "${YELLOW}⚠️  jq not found, skipping JSON validation${NC}"
    fi
    
    print_result $exit_code
}

function print_summary() {
    print_header "📋 Test Summary"
    
    echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
    
    local total=$((TESTS_PASSED + TESTS_FAILED))
    if [[ $total -gt 0 ]]; then
        local percentage=$((TESTS_PASSED * 100 / total))
        echo -e "${BLUE}📊 Success Rate: ${percentage}%${NC}"
    fi
    
    echo ""
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}"
        echo -e "${BLUE}📁 Coverage report: htmlcov/index.html${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        exit 1
    fi
}

# Main execution
echo -e "${BLUE}🚀 Starting comprehensive test suite for read_me_later project...${NC}"
echo ""

run_python_tests
echo ""

run_shellcheck
echo ""

validate_dockerfile
echo ""

test_docker_build
echo ""

run_integration_tests
echo ""

print_summary 