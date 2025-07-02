#!/bin/bash
# Development environment setup script for machine-stats
# Run this script with: source dev-env.sh

echo "Setting up development environment for machine-stats..."

# Initialize pyenv
eval "$(pyenv init -)"

# Check if we're using the correct Python version
current_version=$(python --version 2>&1 | cut -d' ' -f2)
expected_version="3.11.13"

if [[ "$current_version" == "$expected_version" ]]; then
    echo "✓ Using Python $current_version"
else
    echo "⚠ Python version mismatch. Expected $expected_version, got $current_version"
    echo "Setting local Python version to $expected_version..."
    pyenv local $expected_version
fi

# Verify machine-stats is installed in development mode
if pip list | grep -q "machine_stats.*dev0.*$(pwd)"; then
    echo "✓ machine-stats is installed in development mode"
else
    echo "⚠ machine-stats not found in development mode. Installing..."
    pip install -e .
fi

echo "✓ Development environment ready!"
echo ""
echo "You can now use:"
echo "  machine-stats --help"
echo "  machine_stats --help"
echo ""
echo "Any changes you make to the source code will be immediately reflected." 