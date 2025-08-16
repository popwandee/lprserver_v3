#!/bin/bash
"""
AI Camera v1.3 Test Runner Script

This script provides a unified interface for running various tests in the AI Camera v1.3 system.
Users can select from different test categories and individual tests.

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/../venv_hailo"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

log_subheader() {
    echo -e "${CYAN}$1${NC}"
}

# Test categories and their descriptions
declare -A TEST_CATEGORIES=(
    ["1"]="System Integration Tests"
    ["2"]="Component Tests"
    ["3"]="Health Monitoring Tests"
    ["4"]="WebSocket Tests"
    ["5"]="Database Tests"
    ["6"]="Import Validation Tests"
    ["7"]="Production Tests"
    ["8"]="Utility Scripts"
    ["9"]="Run All Tests"
    ["0"]="Exit"
)

# Test files organized by category
declare -A SYSTEM_TESTS=(
    ["1"]="test_auto_startup_sequence.py - Auto-startup sequence testing"
    ["2"]="test_production_startup.py - Production startup testing"
    ["3"]="test_frame_capture.py - Frame capture testing"
    ["4"]="test_imports.py - Import validation testing"
)

declare -A COMPONENT_TESTS=(
    ["1"]="test_detection_models.py - Detection models testing"
    ["2"]="test_attribute_fixes.py - Attribute fixes testing"
    ["3"]="test_status_indicator.py - Status indicator testing"
)

declare -A HEALTH_TESTS=(
    ["1"]="test_health_monitor.py - Health monitor testing"
    ["2"]="test_detection_health_integration.py - Detection-health integration"
    ["3"]="test_health_detection_integration.py - Health-detection integration"
)

declare -A WEBSOCKET_TESTS=(
    ["1"]="test_websocket_client.py - WebSocket client testing"
    ["2"]="test_websocket_server.py - WebSocket server testing"
)

declare -A DATABASE_TESTS=(
    ["1"]="test_progress_pagination.py - Database pagination testing"
    ["2"]="insert_sample_detection_data.py - Insert sample data"
)

declare -A PRODUCTION_TESTS=(
    ["1"]="test_metrics_size.py - Metrics size testing"
)

declare -A UTILITY_SCRIPTS=(
    ["1"]="migrate_absolute_imports.py - Migrate to absolute imports"
    ["2"]="log_rotation.sh - Log rotation utility"
)

# Function to check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" != *"venv_hailo"* ]]; then
        log_warn "Virtual environment not detected. Attempting to activate..."
        if [ -f "$VENV_PATH/bin/activate" ]; then
            source "$VENV_PATH/bin/activate"
            log_info "Virtual environment activated"
        else
            log_error "Virtual environment not found at $VENV_PATH"
            log_info "Please activate your virtual environment manually"
            return 1
        fi
    fi
    return 0
}

# Function to run a single test
run_test() {
    local test_file="$1"
    local test_name="$2"
    
    log_subheader "Running: $test_name"
    log_info "File: $test_file"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run the test
    if [[ "$test_file" == *.py ]]; then
        python3 "$SCRIPT_DIR/$test_file"
    elif [[ "$test_file" == *.sh ]]; then
        bash "$SCRIPT_DIR/$test_file"
    fi
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_info "✓ Test completed successfully"
    else
        log_error "✗ Test failed with exit code $exit_code"
    fi
    
    echo ""
    return $exit_code
}

# Function to show test menu for a category
show_test_menu() {
    local category_name="$1"
    local -n test_list="$2"
    
    log_header "$category_name"
    echo ""
    
    for key in "${!test_list[@]}"; do
        echo -e "${CYAN}$key)${NC} ${test_list[$key]}"
    done
    
    echo -e "${CYAN}0)${NC} Back to main menu"
    echo ""
}

# Function to handle test category selection
handle_test_category() {
    local category="$1"
    
    case $category in
        "1") # System Integration Tests
            show_test_menu "System Integration Tests" SYSTEM_TESTS
            read -p "Select test (0-4): " choice
            case $choice in
                "1") run_test "test_auto_startup_sequence.py" "Auto-startup sequence testing" ;;
                "2") run_test "test_production_startup.py" "Production startup testing" ;;
                "3") run_test "test_frame_capture.py" "Frame capture testing" ;;
                "4") run_test "test_imports.py" "Import validation testing" ;;
                "0") return ;;
                *) log_error "Invalid choice" ;;
            esac
            ;;
        "2") # Component Tests
            show_test_menu "Component Tests" COMPONENT_TESTS
            read -p "Select test (0-3): " choice
            case $choice in
                "1") run_test "test_detection_models.py" "Detection models testing" ;;
                "2") run_test "test_attribute_fixes.py" "Attribute fixes testing" ;;
                "3") run_test "test_status_indicator.py" "Status indicator testing" ;;
                "0") return ;;
                *) log_error "Invalid choice" ;;
            esac
            ;;
        "3") # Health Monitoring Tests
            show_test_menu "Health Monitoring Tests" HEALTH_TESTS
            read -p "Select test (0-3): " choice
            case $choice in
                "1") run_test "test_health_monitor.py" "Health monitor testing" ;;
                "2") run_test "test_detection_health_integration.py" "Detection-health integration" ;;
                "3") run_test "test_health_detection_integration.py" "Health-detection integration" ;;
                "0") return ;;
                *) log_error "Invalid choice" ;;
            esac
            ;;
        "4") # WebSocket Tests
            show_test_menu "WebSocket Tests" WEBSOCKET_TESTS
            read -p "Select test (0-2): " choice
            case $choice in
                "1") run_test "test_websocket_client.py" "WebSocket client testing" ;;
                "2") run_test "test_websocket_server.py" "WebSocket server testing" ;;
                "0") return ;;
                *) log_error "Invalid choice" ;;
            esac
            ;;
        "5") # Database Tests
            show_test_menu "Database Tests" DATABASE_TESTS
            read -p "Select test (0-2): " choice
            case $choice in
                "1") run_test "test_progress_pagination.py" "Database pagination testing" ;;
                "2") run_test "insert_sample_detection_data.py" "Insert sample data" ;;
                "0") return ;;
                *) log_error "Invalid choice" ;;
            esac
            ;;
        "6") # Import Validation Tests
            log_header "Import Validation Tests"
            echo ""
            log_info "Running import validation..."
            run_test "test_imports.py" "Import validation testing"
            ;;
        "7") # Production Tests
            show_test_menu "Production Tests" PRODUCTION_TESTS
            read -p "Select test (0-1): " choice
            case $choice in
                "1") run_test "test_metrics_size.py" "Metrics size testing" ;;
                "0") return ;;
                *) log_error "Invalid choice" ;;
            esac
            ;;
        "8") # Utility Scripts
            show_test_menu "Utility Scripts" UTILITY_SCRIPTS
            read -p "Select script (0-2): " choice
            case $choice in
                "1") run_test "migrate_absolute_imports.py" "Migrate to absolute imports" ;;
                "2") run_test "log_rotation.sh" "Log rotation utility" ;;
                "0") return ;;
                *) log_error "Invalid choice" ;;
            esac
            ;;
        "9") # Run All Tests
            log_header "Running All Tests"
            echo ""
            log_warn "This will run all tests sequentially. This may take a while."
            read -p "Continue? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                run_all_tests
            else
                log_info "Cancelled"
            fi
            ;;
        *) log_error "Invalid category" ;;
    esac
}

# Function to run all tests
run_all_tests() {
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    log_header "Running All Tests"
    echo ""
    
    # System Tests
    log_subheader "System Integration Tests"
    for test_file in "${SYSTEM_TESTS[@]}"; do
        test_file=$(echo "$test_file" | cut -d' ' -f1)
        test_name=$(echo "$test_file" | sed 's/\.py$//' | sed 's/test_//')
        total_tests=$((total_tests + 1))
        
        if run_test "$test_file" "$test_name"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    # Component Tests
    log_subheader "Component Tests"
    for test_file in "${COMPONENT_TESTS[@]}"; do
        test_file=$(echo "$test_file" | cut -d' ' -f1)
        test_name=$(echo "$test_file" | sed 's/\.py$//' | sed 's/test_//')
        total_tests=$((total_tests + 1))
        
        if run_test "$test_file" "$test_name"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    # Health Tests
    log_subheader "Health Monitoring Tests"
    for test_file in "${HEALTH_TESTS[@]}"; do
        test_file=$(echo "$test_file" | cut -d' ' -f1)
        test_name=$(echo "$test_file" | sed 's/\.py$//' | sed 's/test_//')
        total_tests=$((total_tests + 1))
        
        if run_test "$test_file" "$test_name"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    # WebSocket Tests
    log_subheader "WebSocket Tests"
    for test_file in "${WEBSOCKET_TESTS[@]}"; do
        test_file=$(echo "$test_file" | cut -d' ' -f1)
        test_name=$(echo "$test_file" | sed 's/\.py$//' | sed 's/test_//')
        total_tests=$((total_tests + 1))
        
        if run_test "$test_file" "$test_name"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    # Database Tests
    log_subheader "Database Tests"
    for test_file in "${DATABASE_TESTS[@]}"; do
        test_file=$(echo "$test_file" | cut -d' ' -f1)
        test_name=$(echo "$test_file" | sed 's/\.py$//' | sed 's/test_//')
        total_tests=$((total_tests + 1))
        
        if run_test "$test_file" "$test_name"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    # Production Tests
    log_subheader "Production Tests"
    for test_file in "${PRODUCTION_TESTS[@]}"; do
        test_file=$(echo "$test_file" | cut -d' ' -f1)
        test_name=$(echo "$test_file" | sed 's/\.py$//' | sed 's/test_//')
        total_tests=$((total_tests + 1))
        
        if run_test "$test_file" "$test_name"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    # Summary
    log_header "Test Results Summary"
    echo ""
    log_info "Total tests: $total_tests"
    log_info "Passed: $passed_tests"
    log_info "Failed: $failed_tests"
    
    if [ $failed_tests -eq 0 ]; then
        log_info "🎉 All tests passed!"
    else
        log_warn "⚠️  Some tests failed"
    fi
}

# Function to show main menu
show_main_menu() {
    log_header "AI Camera v1.3 Test Runner"
    echo ""
    log_info "Select a test category:"
    echo ""
    
    for key in "${!TEST_CATEGORIES[@]}"; do
        echo -e "${CYAN}$key)${NC} ${TEST_CATEGORIES[$key]}"
    done
    
    echo ""
}

# Main function
main() {
    # Check if we're in the right directory
    if [ ! -f "$SCRIPT_DIR/test_runner.sh" ]; then
        log_error "Please run this script from the v1_3/scripts directory"
        exit 1
    fi
    
    # Check virtual environment
    if ! check_venv; then
        log_error "Virtual environment check failed"
        exit 1
    fi
    
    # Main loop
    while true; do
        show_main_menu
        read -p "Select category (0-9): " choice
        
        case $choice in
            "0")
                log_info "Exiting test runner"
                exit 0
                ;;
            "1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9")
                handle_test_category "$choice"
                ;;
            *)
                log_error "Invalid choice. Please select 0-9."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
        echo ""
    done
}

# Run main function
main "$@"
