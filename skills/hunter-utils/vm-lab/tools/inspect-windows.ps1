# inspect-windows.ps1 <app-name> - one-shot triage of an installed/running Windows
# app. Runs ON the guest (push via rcs, executed with -File). Emits ELECTRON_ASAR=.
param([string]$Q)
$ProgressPreference='SilentlyContinue'

Write-Output "================ APP: $Q ================"
Write-Output "--- installed (Uninstall registry) ---"
$keys='HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
      'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
      'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
$apps = Get-ItemProperty $keys -EA SilentlyContinue |
        Where-Object { $_.DisplayName -like "*$Q*" } |
        Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
$apps | ForEach-Object { Write-Output ("  {0}  {1}  [{2}]" -f $_.DisplayName,$_.DisplayVersion,$_.Publisher) }
$loc = ($apps | Select-Object -First 1).InstallLocation

Write-Output ""; Write-Output "--- running processes ---"
$procs = Get-CimInstance Win32_Process -Filter "Name like '%$Q%'" -EA SilentlyContinue
$procs | ForEach-Object { Write-Output ("  pid={0} ppid={1} {2}" -f $_.ProcessId,$_.ParentProcessId,$_.ExecutablePath) }
if (-not $loc -and $procs) { $loc = Split-Path ($procs | Select -First 1).ExecutablePath -Parent }

# locate main exe
$exe = $null
if ($loc) { $exe = Get-ChildItem $loc -Filter *.exe -EA SilentlyContinue | Where-Object { $_.BaseName -like "*$Q*" } | Select -First 1 -Exp FullName }
if (-not $exe -and $procs) { $exe = ($procs | Select -First 1).ExecutablePath }

Write-Output ""; Write-Output "--- signature / version ---"
if ($exe) {
  Write-Output "  exe: $exe"
  $s = Get-AuthenticodeSignature $exe
  Write-Output ("  sig: {0}  signer: {1}" -f $s.Status, $s.SignerCertificate.Subject)
  $vi = (Get-Item $exe).VersionInfo
  Write-Output ("  ver: {0}  company: {1}" -f $vi.ProductVersion, $vi.CompanyName)
}

Write-Output ""; Write-Output "--- services referencing it ---"
Get-CimInstance Win32_Service -EA SilentlyContinue | Where-Object { $_.PathName -like "*$Q*" } |
  ForEach-Object { Write-Output ("  {0} [{1}] {2}" -f $_.Name,$_.State,$_.PathName) }

Write-Output ""; Write-Output "--- scheduled tasks referencing it ---"
Get-ScheduledTask -EA SilentlyContinue | Where-Object { ($_.Actions.Execute -join ' ') -like "*$Q*" } |
  ForEach-Object { Write-Output ("  {0}" -f $_.TaskName) } | Select -First 10

Write-Output ""; Write-Output "--- loaded modules (non-Windows) of first live pid ---"
if ($procs) {
  $p = Get-Process -Id ($procs | Select -First 1).ProcessId -EA SilentlyContinue
  $p.Modules | Where-Object { $_.FileName -notlike "$env:WINDIR*" } |
    Select-Object -First 15 | ForEach-Object { Write-Output ("  " + $_.FileName) }
}

Write-Output ""; Write-Output "--- bundled runtimes / electron ---"
if ($loc -and (Test-Path $loc)) {
  Get-ChildItem $loc -Recurse -Depth 3 -Include node.exe,bun.exe,app.asar -EA SilentlyContinue |
    ForEach-Object { Write-Output ("  " + $_.FullName) } | Select -First 10
  $asar = Get-ChildItem $loc -Recurse -Depth 3 -Filter app.asar -EA SilentlyContinue | Select -First 1
  if ($asar) { Write-Output ("ELECTRON_ASAR=" + $asar.FullName) }
}
