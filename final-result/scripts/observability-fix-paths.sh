#!/bin/bash
# Helper script to fix observability paths after cloning this repo
# Updates .claude/.observability-config with the correct multi-agent-workflow path

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/.claude/.observability-config"

echo "=========================================="
echo "Fix Observability Paths"
echo "=========================================="
echo ""
echo "This script will update the observability configuration to point to"
echo "your multi-agent-workflow repository location."
echo ""

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    echo "This script should be run from a project with observability already configured."
    exit 1
fi

# Show current configuration
echo "Current configuration:"
if command -v jq &> /dev/null; then
    CURRENT_PATH=$(jq -r '.MULTI_AGENT_WORKFLOW_PATH' "$CONFIG_FILE" 2>/dev/null || echo "Unable to read")
    echo "  Multi-Agent Workflow Path: $CURRENT_PATH"
else
    echo "  (jq not installed, cannot display current path)"
fi
echo ""

# Prompt for new path
DEFAULT_PATH="$HOME/multi-agent-workflow"
read -p "Enter the path to your multi-agent-workflow repo [$DEFAULT_PATH]: " NEW_PATH
NEW_PATH="${NEW_PATH:-$DEFAULT_PATH}"

# Expand tilde
NEW_PATH="${NEW_PATH/#\~/$HOME}"

# Validate path exists
if [ ! -d "$NEW_PATH" ]; then
    echo ""
    echo "Warning: Directory does not exist: $NEW_PATH"
    read -p "Do you want to continue anyway? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Validate it looks like the right repo
if [ -d "$NEW_PATH" ] && [ ! -f "$NEW_PATH/scripts/observability-start.sh" ]; then
    echo ""
    echo "Warning: $NEW_PATH doesn't appear to be the multi-agent-workflow repo"
    echo "  (scripts/observability-start.sh not found)"
    read -p "Do you want to continue anyway? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Backup existing config
BACKUP_FILE="$CONFIG_FILE.backup-$(date +%Y%m%d-%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo ""
echo "Backup created: $BACKUP_FILE"

# Update config file
SERVER_URL="http://localhost:4000"
CLIENT_URL="http://localhost:5173"

cat > "$CONFIG_FILE" << EOF
{
  "MULTI_AGENT_WORKFLOW_PATH": "$NEW_PATH",
  "SERVER_URL": "$SERVER_URL",
  "CLIENT_URL": "$CLIENT_URL"
}
EOF

echo ""
echo "✅ Configuration updated successfully!"
echo ""
echo "Updated configuration:"
echo "  Multi-Agent Workflow Path: $NEW_PATH"
echo "  Server URL: $SERVER_URL"
echo "  Client URL: $CLIENT_URL"
echo ""
echo "Next steps:"
echo "  1. Start the observability server:"
echo "     cd $NEW_PATH"
echo "     ./scripts/observability-start.sh"
echo ""
echo "  2. Restart Claude Code to load the new configuration"
echo ""
echo "  3. The observability dashboard will be available at:"
echo "     $CLIENT_URL"
echo ""
