#!/bin/bash
# Convenient test runner script

set -e

echo "🧪 MTG Madness Simulator - Test Runner"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
MODE=${1:-"all"}

case $MODE in
  "all")
    echo -e "${BLUE}Running all tests...${NC}"
    pytest test_madness.py -v
    ;;
  
  "coverage")
    echo -e "${BLUE}Running tests with coverage report...${NC}"
    pytest test_madness.py --cov=madness --cov-report=html --cov-report=term -v
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
    ;;
  
  "quick")
    echo -e "${BLUE}Running quick tests (no statistical tests)...${NC}"
    pytest test_madness.py -v -m "not statistical"
    ;;
  
  "unit")
    echo -e "${BLUE}Running unit tests only...${NC}"
    pytest test_madness.py -v -k "not integration"
    ;;
  
  "watch")
    echo -e "${BLUE}Running tests in watch mode...${NC}"
    pytest-watch test_madness.py -v
    ;;
  
  "debug")
    echo -e "${BLUE}Running tests with debugger on failure...${NC}"
    pytest test_madness.py -v --pdb
    ;;
  
  *)
    echo "Usage: ./run_tests.sh [all|coverage|quick|unit|watch|debug]"
    echo ""
    echo "Options:"
    echo "  all       - Run all tests (default)"
    echo "  coverage  - Run tests with coverage report"
    echo "  quick     - Run fast tests only"
    echo "  unit      - Run unit tests only"
    echo "  watch     - Run tests in watch mode (requires pytest-watch)"
    echo "  debug     - Run tests with debugger on failure"
    exit 1
    ;;
esac

echo -e "${GREEN}✅ Test run completed${NC}"

