#!/bin/bash

set -e

echo "🔒 Security Audit Skills Installer"
echo ""

if [ -d ".context" ]; then
  echo "ℹ️  .context directory already exists, skipping clone"
else
  echo "Cloning .context repository..."
  if ! git clone https://github.com/forefy/.context > /dev/null 2>&1; then
    echo "❌ Failed to clone repository. Check your internet connection."
    exit 1
  fi
fi

echo ""
echo "Select your platform:"
echo "1) Copilot CLI (copilot)"
echo "2) GitHub Copilot (VSCode/IDE)"
echo "3) Claude Code"
echo ""
read -p "Choice [1-3]: " choice </dev/tty

GIT_REPO=false
if [ -d ".git" ]; then
  GIT_REPO=true
fi

case $choice in
  1)
    echo "Installing for Copilot CLI..."
    mkdir -p .claude/skills/
    cp -r .context/skills/* .claude/skills/
    echo "✓ Skills copied to .claude/skills/"
    echo "✓ Use with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo ""
    echo "To start: copilot"
    ;;
  2)
    echo "Installing for GitHub Copilot (VSCode/IDE)..."
    mkdir -p .claude/skills/ .github/prompts/
    
    cp -r .context/skills/* .claude/skills/
    cp .context/prompts/*.prompt.md .github/prompts/ 2>/dev/null || true
    
    echo "✓ Skills copied to .claude/skills/"
    echo "✓ Prompts copied to .github/prompts/"
    echo "✓ Use skills with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo "✓ Use prompts with: /generate_audit_report_generic"
    ;;
  3)
    echo "Installing for Claude Code..."
    mkdir -p .claude/skills/
    
    cp -r .context/skills/* .claude/skills/
    
    echo "✓ Skills copied to .claude/skills/"
    echo "✓ Use with: @smart-contract-security-audit or @infrastructure-security-audit"
    echo ""
    echo "To start: claude"
    ;;
  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "✅ Installation complete!"
