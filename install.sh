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
    echo "✓ Use with: @security-review-solidity"
    echo ""
    echo "To start: copilot"
    ;;
  2)
    echo "Installing for GitHub Copilot (VSCode/IDE)..."
    mkdir -p .claude/skills/
    
    cp -r .context/skills/* .claude/skills/
    
    if [ "$GIT_REPO" = true ]; then
      mkdir -p .github/ .github/prompts/
      
      if [ -f ".github/copilot-instructions.md" ]; then
        echo "⚠️  .github/copilot-instructions.md already exists"
        read -p "Overwrite? [y/N]: " overwrite </dev/tty
        if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
          echo "Skipped."
          exit 0
        fi
      fi
      
      echo "Select skill:"
      echo "1) Smart Contract Audit"
      echo "2) Infrastructure Audit"
      read -p "Choice [1-2]: " skill </dev/tty
      if [ "$skill" = "1" ]; then
        cp .context/skills/smart-contract-security-audit/SKILL.md .github/copilot-instructions.md
      else
        cp .context/skills/infrastructure-security-audit/SKILL.md .github/copilot-instructions.md
      fi
      
      cp .context/prompts/*.prompt.md .github/prompts/ 2>/dev/null || true
      
      echo "✓ Instructions copied to .github/copilot-instructions.md"
      echo "✓ Skills copied to .claude/skills/"
      echo "✓ Prompts copied to .github/prompts/"
      echo "✓ Use skills with: @security-review-solidity"
      echo "✓ Use prompts with: /generate_audit_report_generic"
    else
      echo "ℹ️  Not in git repository - skipping .github/ setup"
      echo "✓ Skills copied to .claude/skills/"
      echo "✓ Use skills with: @security-review-solidity"
    fi
    ;;
  3)
    echo "Installing for Claude Code..."
    mkdir -p .claude/commands/ .claude/skills/
    
    cp -r .context/skills/* .claude/skills/
    
    if [ -f ".claude/commands/audit.md" ]; then
      echo "⚠️  .claude/commands/audit.md already exists"
      read -p "Overwrite? [y/N]: " overwrite </dev/tty
      if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Skipped."
        exit 0
      fi
    fi
    
    echo "Select skill:"
    echo "1) Solidity"
    echo "2) Anchor"
    echo "3) Vyper"
    read -p "Choice [1-3]: " lang </dev/tty
    case $lang in
      1) cp .context/skills/security-review-solidity/SKILL.md .claude/commands/audit.md ;;
      2) cp .context/skills/security-review-anchor/SKILL.md .claude/commands/audit.md ;;
      3) cp .context/skills/security-review-vyper/SKILL.md .claude/commands/audit.md ;;
    esac
    echo "✓ Command copied to .claude/commands/audit.md"
    echo "✓ Skills copied to .claude/skills/"
    echo "✓ Run with: claude audit"
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
