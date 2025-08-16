#!/bin/bash
# GitHub Issues Import Runner Script
# This script makes it easy to run the import process with environment variables

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_status "Please copy env.example to .env and fill in your GitHub token:"
    echo "  cp env.example .env"
    echo "  # Then edit .env and add your GITHUB_TOKEN"
    exit 1
fi

# Load environment variables
print_status "Loading environment variables from .env file..."
source .env

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    print_error "GITHUB_TOKEN not found in .env file!"
    print_status "Please add your GitHub token to the .env file:"
    echo "  GITHUB_TOKEN=your_token_here"
    exit 1
fi

# Check if GITHUB_REPO is set
if [ -z "$GITHUB_REPO" ]; then
    print_error "GITHUB_REPO not found in .env file!"
    print_status "Please add your repository name to the .env file:"
    echo "  GITHUB_REPO=your_username/your_repository_name"
    exit 1
fi

# Set default values
ISSUES_FILE=${ISSUES_FILE:-".github/ISSUES_FROM_PLAN.md"}
DRY_RUN=${DRY_RUN:-"false"}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --file)
            ISSUES_FILE="$2"
            shift 2
            ;;
        --manage)
            MANAGE_MODE="true"
            shift
            ;;
        --interactive)
            INTERACTIVE_MODE="true"
            shift
            ;;
        --hardware)
            HARDWARE_NAME="$2"
            shift 2
            ;;
        --component)
            COMPONENT_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Run in dry-run mode (don't create issues)"
            echo "  --file FILE  Specify issues file path (default: .github/ISSUES_FROM_PLAN.md)"
            echo "  --manage     Manage issues (add new ones, check duplicates)"
            echo "  --interactive Interactive issue creation"
            echo "  --hardware NAME Create hardware integration issue"
            echo "  --component NAME Component for hardware integration"
            echo "  --help       Show this help message"
            echo ""
            echo "Environment variables (in .env file):"
            echo "  GITHUB_TOKEN    GitHub personal access token"
            echo "  GITHUB_REPO     Repository name (owner/repo)"
            echo "  ISSUES_FILE     Issues file path (optional)"
            echo "  DRY_RUN         Set to 'true' for dry-run mode (optional)"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Import existing issues"
            echo "  $0 --dry-run                         # Test import without creating"
            echo "  $0 --manage --interactive            # Interactive issue creation"
            echo "  $0 --manage --hardware 'New Camera' --component edge"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if Python scripts exist
if [ ! -f "scripts/import_github_issues.py" ]; then
    print_error "Import script not found: scripts/import_github_issues.py"
    exit 1
fi

if [ ! -f "scripts/setup_labels.py" ]; then
    print_error "Labels script not found: scripts/setup_labels.py"
    exit 1
fi

if [ ! -f "scripts/manage_issues.py" ]; then
    print_error "Manage script not found: scripts/manage_issues.py"
    exit 1
fi

# Make scripts executable
chmod +x scripts/import_github_issues.py
chmod +x scripts/setup_labels.py
chmod +x scripts/manage_issues.py

# Install Python dependencies if needed
print_status "Checking Python dependencies..."
if ! python3 -c "import requests, yaml" 2>/dev/null; then
    print_warning "Required Python packages not found. Installing..."
    pip3 install requests pyyaml python-dotenv
fi

# Check if we're in manage mode
if [ "$MANAGE_MODE" = "true" ]; then
    print_status "Managing GitHub issues..."
    
    if [ "$INTERACTIVE_MODE" = "true" ]; then
        print_status "Starting interactive issue creation..."
        python3 scripts/manage_issues.py --repo "$GITHUB_REPO" --interactive
    elif [ -n "$HARDWARE_NAME" ]; then
        if [ -z "$COMPONENT_NAME" ]; then
            print_error "Component is required for hardware integration!"
            echo "Example: $0 --manage --hardware 'New Camera' --component edge"
            exit 1
        fi
        print_status "Creating hardware integration issue for $HARDWARE_NAME with $COMPONENT_NAME..."
        python3 scripts/manage_issues.py --repo "$GITHUB_REPO" --hardware "$HARDWARE_NAME" --component "$COMPONENT_NAME"
    else
        print_status "Available management options:"
        echo "  --interactive    Interactive issue creation"
        echo "  --hardware NAME --component NAME    Hardware integration issue"
        echo ""
        echo "Examples:"
        echo "  $0 --manage --interactive"
        echo "  $0 --manage --hardware 'New Camera' --component edge"
    fi
    
    print_success "Issue management completed!"
    exit 0
fi

# Check if issues file exists
if [ ! -f "$ISSUES_FILE" ]; then
    print_error "Issues file not found: $ISSUES_FILE"
    exit 1
fi

print_status "Configuration:"
echo "  Repository: $GITHUB_REPO"
echo "  Issues file: $ISSUES_FILE"
echo "  Dry run: $DRY_RUN"

# Setup labels first
print_status "Setting up GitHub labels..."
if [ "$DRY_RUN" = "true" ]; then
    python3 scripts/setup_labels.py --repo "$GITHUB_REPO" --dry-run
else
    python3 scripts/setup_labels.py --repo "$GITHUB_REPO"
fi

# Import issues
print_status "Importing GitHub issues..."
if [ "$DRY_RUN" = "true" ]; then
    python3 scripts/import_github_issues.py --repo "$GITHUB_REPO" --file "$ISSUES_FILE" --dry-run
else
    python3 scripts/import_github_issues.py --repo "$GITHUB_REPO" --file "$ISSUES_FILE"
fi

print_success "Import process completed!"
