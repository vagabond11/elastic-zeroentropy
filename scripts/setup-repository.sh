#!/bin/bash

# Repository Setup Script for elastic-zeroentropy
# This script helps set up all the professional repository features

set -e

echo "🚀 Setting up elastic-zeroentropy repository..."

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

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "This script must be run from the repository root directory"
    exit 1
fi

print_status "Setting up repository features..."

# Create necessary directories
print_status "Creating directories..."
mkdir -p scripts
mkdir -p docs
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p .github/workflows

print_success "Directories created"

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git repository not found. Please initialize git first."
    exit 1
fi

# Check if remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    print_warning "No remote origin found. Please add your GitHub repository as origin."
    echo "Example: git remote add origin https://github.com/yourusername/elastic-zeroentropy.git"
fi

print_status "Repository setup complete!"
print_status ""
print_status "Next steps:"
print_status "1. Push your changes to GitHub:"
print_status "   git add . && git commit -m 'Add professional repository features' && git push origin main"
print_status ""
print_status "2. On GitHub, enable these features:"
print_status "   - Issues"
print_status "   - Projects"
print_status "   - Discussions"
print_status "   - Dependabot alerts"
print_status "   - Security advisories"
print_status ""
print_status "3. Set up branch protection rules for main branch"
print_status "4. Configure repository topics and description"
print_status "5. Set up repository secrets for CI/CD"
print_status ""
print_status "Repository is now ready for professional development! 🎉" 