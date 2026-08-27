# Unattended / seed installs (Path B - no console typing)

The robust way to get a fresh guest to SSH without fighting the GUI console: bake
sshd + your public key into the OS install itself. You supply the ISO; these seed
files do the rest.

## Linux - cloud-init (best)
Most distros ship a cloud image. Provide a `user-data` file on a seed ISO (label
`cidata`) alongside an empty `meta-data`:
```yaml
#cloud-config
users:
  - name: lab
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-ed25519 AAAA...REPLACE_ME... vmlab
ssh_pwauth: false
package_update: true
packages: [openssh-server, strace, gdb, lsof, tcpdump]
```
Build the seed ISO:
```bash
cloud-localds seed.iso user-data meta-data     # or: mkisofs -o seed.iso -V cidata -J -r user-data meta-data
```
- **VirtualBox** has native unattended install that generates this for you:
  `VBoxManage unattended install <vm> --iso=<distro.iso> --user=lab \
    --ssh-key=~/.ssh/vmlab_ed25519.pub --install-additions`.
- **VMware / Parallels**: attach `seed.iso` as a second CD and boot the cloud image.

## Windows - autounattend.xml
Put an `autounattend.xml` on a FAT32 USB/ISO; Setup auto-detects it. Include a
`<FirstLogonCommands>` that runs the same steps as `windows.ps1`:
```xml
<FirstLogonCommands>
  <SynchronousCommand><Order>1</Order>
    <CommandLine>powershell -ExecutionPolicy Bypass -Command "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0; Set-Service sshd -StartupType Automatic; Start-Service sshd"</CommandLine>
  </SynchronousCommand>
  <SynchronousCommand><Order>2</Order>
    <CommandLine>powershell -ExecutionPolicy Bypass -Command "Set-Content $env:ProgramData\ssh\administrators_authorized_keys 'ssh-ed25519 AAAA...REPLACE_ME... vmlab' -Encoding ascii; icacls $env:ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant Administrators:F /grant SYSTEM:F"</CommandLine>
  </SynchronousCommand>
</FirstLogonCommands>
```
Generate the full file with the Windows SIM, or start from the many public
autounattend generators. For Windows 11 ARM64 use the ARM64 ISO.

## macOS
No supported unattended install for guests. Do Path A once (`macos.sh` + Remote
Login toggle), enable auto-login (see toolkits/macos.md), then **snapshot** - that
snapshot is your reusable "already bootstrapped" baseline.

## Where to get ISOs (you supply these)
- **Windows 11** (x64 & ARM64): Microsoft's official ISO / Download Windows 11 page.
- **Linux**: the distro's cloud image (Ubuntu cloud-images, Fedora Cloud, Debian genericcloud).
- **macOS**: `mist list` / `mist download` or `softwareupdate --fetch-full-installer`
  on a Mac, then build the `.ipsw`/installer for Parallels/Fusion.
