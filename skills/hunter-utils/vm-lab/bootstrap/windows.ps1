# bootstrap/windows.ps1 - paste into Terminal (Admin) / PowerShell ON THE WINDOWS GUEST.
# Installs OpenSSH server, opens the firewall, seeds the admin key, PS as default shell.
# Replace $Pub with your ~/.ssh/vmlab_ed25519.pub. Pick the ARM64 or x64 asset to
# match the guest arch (auto-detected below).

$Pub = 'ssh-ed25519 AAAA...REPLACE_ME... vmlab'

$ProgressPreference='SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12

# Try the built-in capability first; if FoD won't fetch (common on fresh VMs:
# 0x800f0950 / 0x800f0954), fall back to the GitHub Win32-OpenSSH release.
$ok = $false
try { Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -EA Stop; $ok=$true } catch {}
if (-not $ok) {
  $arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {'ARM64'} else {'Win64'}
  $url  = "https://github.com/PowerShell/Win32-OpenSSH/releases/download/10.0.0.0p2-Preview/OpenSSH-$arch.zip"
  $z="$env:TEMP\OpenSSH.zip"; Invoke-WebRequest $url -OutFile $z
  Expand-Archive $z "$env:ProgramFiles\OpenSSH" -Force
  $d=(Get-ChildItem "$env:ProgramFiles\OpenSSH" -Recurse -Filter sshd.exe | Select -First 1).DirectoryName
  & powershell -ExecutionPolicy Bypass -File (Join-Path $d 'install-sshd.ps1')
}
Set-Service sshd -StartupType Automatic; Start-Service sshd
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server' -Enabled True `
  -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -EA SilentlyContinue | Out-Null

# Admin key auth requires administrators_authorized_keys with a locked-down ACL:
$f="$env:ProgramData\ssh\administrators_authorized_keys"
Set-Content $f $Pub -Encoding ascii
icacls $f /inheritance:r /grant 'Administrators:F' /grant 'SYSTEM:F' | Out-Null

# Land SSH sessions in PowerShell (nicer than cmd) for run_win to target:
reg add "HKLM\SOFTWARE\OpenSSH" /v DefaultShell /t REG_SZ `
  /d "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" /f | Out-Null
Write-Host "sshd up, key seeded. Test from host, then snapshot."
