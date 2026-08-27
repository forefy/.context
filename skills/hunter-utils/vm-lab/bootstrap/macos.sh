#!/usr/bin/env bash
# bootstrap/macos.sh - paste this into Terminal ON THE macOS GUEST console.
# Replace PUBKEY with the contents of your ~/.ssh/vmlab_ed25519.pub (host side).
# After this: flip Remote Login on in the GUI, then everything is over SSH.

PUBKEY='ssh-ed25519 AAAA...REPLACE_ME... vmlab'

mkdir -p ~/.ssh && chmod 700 ~/.ssh
printf '%s\n' "$PUBKEY" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "key installed. Now: System Settings > General > Sharing > Remote Login = ON"
# NOTE: `sudo systemsetup -setremotelogin on` fails on macOS 26 from Terminal
# ("requires Full Disk Access") - use the GUI toggle above. One time only, then snapshot.
