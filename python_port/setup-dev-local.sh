#!/bin/bash
# Setup script to run openspec from local development folder using uvx

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OPENSPEC_DEV_DIR="$SCRIPT_DIR"

echo "Setting up OpenSpec to run from development folder: $OPENSPEC_DEV_DIR"
echo ""

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "Error: uvx is not installed"
    echo "Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Detect shell config file
if [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_CONFIG="$HOME/.bash_profile"
else
    echo "Warning: Could not find shell config file (.bashrc, .zshrc, or .bash_profile)"
    echo "Please manually add the alias to your shell config file"
    SHELL_CONFIG=""
fi

# Create the alias
ALIAS_LINE="# OpenSpec development - run from local folder"
ALIAS_CODE="alias openspec='uvx --from \"$OPENSPEC_DEV_DIR\" openspec'"

# Check if already added
if [ -n "$SHELL_CONFIG" ]; then
    if grep -q "OpenSpec development - run from local folder" "$SHELL_CONFIG" 2>/dev/null; then
        echo "⚠ OpenSpec alias already exists in $SHELL_CONFIG"
        echo "Skipping addition to shell config."
    else
        echo "Adding OpenSpec alias to $SHELL_CONFIG..."
        echo "" >> "$SHELL_CONFIG"
        echo "$ALIAS_LINE" >> "$SHELL_CONFIG"
        echo "$ALIAS_CODE" >> "$SHELL_CONFIG"
        echo "✓ Added to $SHELL_CONFIG"
    fi
else
    echo "Please add this to your shell config file:"
    echo ""
    echo "$ALIAS_LINE"
    echo "$ALIAS_CODE"
    echo ""
fi

echo ""
echo "Setup complete!"
echo ""
echo "To use OpenSpec from this development folder:"
echo "  1. Reload your shell: source $SHELL_CONFIG"
echo "  2. Run: openspec --version"
echo ""
echo "The 'openspec' command will now run from: $OPENSPEC_DEV_DIR"
echo "This works from any directory!"

