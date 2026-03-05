#!/bin/bash

set -e

echo "Security Audit Skills Installer"
echo ""

echo "Select your platform:"
echo "1) Claude Code"
echo "2) Copilot CLI"
echo "3) GitHub Copilot (VSCode)"
echo ""
read -p "Choice [1-3]: " choice </dev/tty

echo ""
echo "Select install location:"
echo "1) Global (~/.claude/skills) [default]"
echo "2) Current project ($(pwd))"
echo "3) Custom path"
echo ""
read -p "Choice [1-3] (Enter for default): " location_choice </dev/tty
location_choice="${location_choice:-1}"

case $location_choice in
  1)
    INSTALL_BASE="$HOME"
    ;;
  2)
    INSTALL_BASE="$(pwd)"
    ;;
  3)
    read -p "Enter path: " custom_path </dev/tty
    INSTALL_BASE="$custom_path"
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

CONTEXT_DIR="$INSTALL_BASE/.context"

if [ -d "$CONTEXT_DIR" ]; then
  echo "Updating existing installation at $CONTEXT_DIR..."
  cd "$CONTEXT_DIR" && git pull --quiet && cd - > /dev/null
else
  echo "Installing to $CONTEXT_DIR..."
  if ! git clone https://github.com/forefy/.context "$CONTEXT_DIR" > /dev/null 2>&1; then
    echo "Failed to clone repository. Check your internet connection."
    exit 1
  fi
fi

case $choice in
  1)
    echo "Installing for Claude Code..."
    mkdir -p "$INSTALL_BASE/.claude/skills/"
    cp -r "$CONTEXT_DIR/skills/"* "$INSTALL_BASE/.claude/skills/"
    echo "Skills copied to $INSTALL_BASE/.claude/skills/"
    echo "Use with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo ""
    echo "To start: claude"
    ;;
  2)
    echo "Installing for Copilot CLI..."
    mkdir -p "$INSTALL_BASE/.claude/skills/"
    cp -r "$CONTEXT_DIR/skills/"* "$INSTALL_BASE/.claude/skills/"
    echo "Skills copied to $INSTALL_BASE/.claude/skills/"
    echo "Use with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo ""
    echo "To start: copilot"
    ;;
  3)
    echo "Installing for GitHub Copilot (VSCode)..."
    mkdir -p "$INSTALL_BASE/.claude/skills/" "$INSTALL_BASE/.github/prompts/"
    cp -r "$CONTEXT_DIR/skills/"* "$INSTALL_BASE/.claude/skills/"
    cp "$CONTEXT_DIR/prompts/"*.prompt.md "$INSTALL_BASE/.github/prompts/" 2>/dev/null || true
    echo "Skills copied to $INSTALL_BASE/.claude/skills/"
    echo "Prompts copied to $INSTALL_BASE/.github/prompts/"
    echo "Use skills with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo "Use prompts with: /generate_audit_report_generic"
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "Installation complete!"
