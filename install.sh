#!/bin/bash

set -e

echo "Security Audit Skills Installer"
echo ""

if [ -d ".context" ]; then
    echo "ℹ  .context directory already exists, skipping clone"
else
  echo "Cloning .context repository..."
  if ! git clone https://github.com/forefy/.context > /dev/null 2>&1; then
    echo "Failed to clone repository. Check your internet connection."
    exit 1
  fi
fi

echo ""
echo "Select your platform:"
echo "1) Claude Code"
echo "2) Copilot CLI"
echo "3) GitHub Copilot (VSCode)"
echo ""
read -p "Choice [1-3]: " choice </dev/tty


get_install_base() {
  echo ""
  echo "Select install location:"
  echo "1) Current project"
  echo "2) Custom path"
  echo "3) Global (~/.claude/skills/)"
  echo ""
  read -p "Choice [1-3]: " location_choice </dev/tty

  case $location_choice in
    1)
      INSTALL_BASE="."
      ;;
    2)
      read -p "Enter path: " custom_path </dev/tty
      INSTALL_BASE="$custom_path"
      ;;
    3)
      INSTALL_BASE="$HOME"
      ;;
    *)
      echo "Invalid choice"
      exit 1
      ;;
  esac
}

case $choice in
  1)
    echo "Installing for Claude Code..."
    get_install_base
    mkdir -p "$INSTALL_BASE/.claude/skills/"
    cp -r .context/skills/* "$INSTALL_BASE/.claude/skills/"
    echo "Skills copied to $INSTALL_BASE/.claude/skills/"
    echo "Use with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo ""
    echo "To start: claude"
    ;;
  2)
    echo "Installing for Copilot CLI..."
    get_install_base
    mkdir -p "$INSTALL_BASE/.claude/skills/"
    cp -r .context/skills/* "$INSTALL_BASE/.claude/skills/"
    echo "Skills copied to $INSTALL_BASE/.claude/skills/"
    echo "Use with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo ""
    echo "To start: copilot"
    ;;
  3)
    echo "Installing for GitHub Copilot (VSCode)..."
    mkdir -p .claude/skills/ .github/prompts/
    cp -r .context/skills/* .claude/skills/
    cp .context/prompts/*.prompt.md .github/prompts/ 2>/dev/null || true
    echo "Skills copied to .claude/skills/"
    echo "Prompts copied to .github/prompts/"
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
