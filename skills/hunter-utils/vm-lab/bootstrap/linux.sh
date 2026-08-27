#!/usr/bin/env bash
# bootstrap/linux.sh - paste into a terminal ON THE LINUX GUEST console (or send via
# VirtualBox prov_type). Replace PUBKEY. Installs sshd, enables it, seeds the key.
# Most cloud images already have sshd + your key (see unattended.md) - then skip this.

PUBKEY='ssh-ed25519 AAAA...REPLACE_ME... vmlab'

set -e
if command -v apt-get >/dev/null; then sudo apt-get update && sudo apt-get install -y openssh-server
elif command -v dnf >/dev/null;   then sudo dnf install -y openssh-server
elif command -v pacman >/dev/null; then sudo pacman -S --noconfirm openssh
fi
sudo systemctl enable --now ssh 2>/dev/null || sudo systemctl enable --now sshd
mkdir -p ~/.ssh && chmod 700 ~/.ssh
printf '%s\n' "$PUBKEY" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
echo "sshd up, key seeded. Test from host, then snapshot."
