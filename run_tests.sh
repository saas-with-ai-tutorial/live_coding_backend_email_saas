#!/bin/bash

# Test runner script for Email SaaS backend
# This script runs the test suite with various options

set -e  # Exit on error

echo "=================================="
echo "Email SaaS Backend - Test Runner"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}Warning: Virtual environment not found. Using system Python.${NC}"
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest is not installed. Installing test dependencies...${NC}"
    pip install -r requirements.txt
fi

echo ""

# Parse command line arguments
case "${1:-all}" in
    all)
        echo -e "${BLUE}Running all tests...${NC}"
        pytest -v
        ;;
    
    coverage)
        echo -e "${BLUE}Running tests with coverage report...${NC}"
        pytest --cov=src --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    email-processor)
        echo -e "${BLUE}Running EmailProcessor tests only...${NC}"
        pytest tests/test_email_processor.py -v
        ;;
    
    gmail-helper)
        echo -e "${BLUE}Running GmailHelper tests only...${NC}"
        pytest tests/test_gmail_helper.py -v
        ;;
    
    unit)
        echo -e "${BLUE}Running unit tests only...${NC}"
        pytest -m unit -v
        ;;
    
    integration)
        echo -e "${BLUE}Running integration tests only...${NC}"
        pytest -m integration -v
        ;;
    
    fast)
        echo -e "${BLUE}Running fast tests (excluding slow tests)...${NC}"
        pytest -m "not slow" -v
        ;;
    
    watch)
        echo -e "${BLUE}Running tests in watch mode...${NC}"
        pytest-watch
        ;;
    
    debug)
        echo -e "${BLUE}Running tests with debug output...${NC}"
        pytest -vv -s
        ;;
    
    *)
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all             - Run all tests (default)"
        echo "  coverage        - Run tests with coverage report"
        echo "  email-processor - Run EmailProcessor tests only"
        echo "  gmail-helper    - Run GmailHelper tests only"
        echo "  unit           - Run unit tests only"
        echo "  integration    - Run integration tests only"
        echo "  fast           - Run fast tests (exclude slow tests)"
        echo "  watch          - Run tests in watch mode"
        echo "  debug          - Run tests with verbose debug output"
        echo ""
        exit 1
        ;;
esac

# Check test result
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed.${NC}"
    exit 1
fi
