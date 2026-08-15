# Windows Endpoint Threat Hunt - Command Reference

> T1 = standard user (no UAC elevation) | T2 = Administrator / elevated PowerShell

---

## Contents

- [Phase 1: Process Activity](#phase-1-process-activity)
  - [1.1 - Recent Processes with Full Details](#11--recent-processes-with-full-details)
  - [1.2 - Process Details with Command Lines and Parent PIDs](#12--process-details-with-command-lines-and-parent-pids)
  - [1.3 - Processes Running from Suspicious Locations](#13--processes-running-from-suspicious-locations)
  - [1.4 - Authenticode Signature Verification for Running Processes](#14--authenticode-signature-verification-for-running-processes)
  - [1.5 - Parent Process Anomalies](#15--parent-process-anomalies)
- [Phase 2: Network Activity](#phase-2-network-activity)
  - [2.1 - Listening Ports](#21--listening-ports)
  - [2.2 - Established Outbound Connections](#22--established-outbound-connections)
  - [2.3 - DNS Cache](#23--dns-cache)
  - [2.4 - HOSTS File](#24--hosts-file)
- [Phase 3: Persistence Mechanisms](#phase-3-persistence-mechanisms)
  - [3.1 - Registry Run Keys](#31--registry-run-keys)
  - [3.2 - Winlogon and BootExecute](#32--winlogon-and-bootexecute)
  - [3.3 - Startup Folders](#33--startup-folders)
  - [3.4 - Scheduled Tasks](#34--scheduled-tasks)
  - [3.5 - Running Services with Full Paths](#35--running-services-with-full-paths)
  - [3.6 - WMI Event Subscriptions (Critical - High Fidelity IOC)](#36--wmi-event-subscriptions-critical--high-fidelity-ioc)
- [Phase 4: File Activity](#phase-4-file-activity)
  - [4.1 - Executable Files in Temp Locations](#41--executable-files-in-temp-locations)
  - [4.2 - Authenticode Verification for Suspicious Files](#42--authenticode-verification-for-suspicious-files)
  - [4.3 - VBScript/JScript/HTA Artifacts](#43--vbscriptjscripthta-artifacts)
- [Phase 5: User & Account Activity](#phase-5-user--account-activity)
  - [5.1 - Local User Accounts](#51--local-user-accounts)
  - [5.2 - Local Administrators Group](#52--local-administrators-group)
  - [5.3 - T2: Windows Security Event Log - Authentication Events](#53--t2-windows-security-event-log--authentication-events)
- [Phase 6: Driver Activity](#phase-6-driver-activity)
  - [6.1 - T2: Driver Query](#61--t2-driver-query)
  - [6.2 - T2: Named Pipes (C2 Framework Indicator)](#62--t2-named-pipes-c2-framework-indicator)
- [Phase 7: Script & Command Execution](#phase-7-script--command-execution)
  - [7.1 - PowerShell Command History](#71--powershell-command-history)
  - [7.2 - T2: PowerShell Script Block Logging (Event 4104)](#72--t2-powershell-script-block-logging-event-4104)
  - [7.3 - PowerShell Transcription Logs](#73--powershell-transcription-logs)
  - [7.4 - BITS Transfer Jobs](#74--bits-transfer-jobs)
- [Phase 8: EDR/Security Tool Status](#phase-8-edrsecurity-tool-status)
  - [8.1 - Windows Defender Status](#81--windows-defender-status)
  - [8.2 - Third-Party EDR Agent Processes](#82--third-party-edr-agent-processes)
  - [8.3 - T2: Security Audit Policy](#83--t2-security-audit-policy)
- [Quick Reference: Windows IOC Severity Ratings](#quick-reference-windows-ioc-severity-ratings)

---

## Phase 1: Process Activity


---

### 1.1 - Recent Processes with Full Details
**Tier:** T1  

```powershell
Get-Process | Select-Object Name, Id, Path, Company, StartTime, CPU, WorkingSet | Sort-Object StartTime -Descending | Select-Object -First 50 | Format-Table -AutoSize
```

**Flag:**
- `Path` in `%TEMP%`, `%APPDATA%`, `%LOCALAPPDATA%`, `C:\Users\*\Downloads`, `ProgramData` - non-std install path
- `Company` empty - unsigned or unknown binary
- `StartTime` very recent + unexpected
- Multiple `powershell.exe`, `cmd.exe`, `wscript.exe`, `cscript.exe` - check cmdlines
- `svchost.exe` not from `C:\Windows\System32\` - process masquerading

---

### 1.2 - Process Details with Command Lines and Parent PIDs
**Tier:** T1 (limited) / T2 (full)  

```powershell
Get-WmiObject Win32_Process | Select-Object Name, ProcessId, ParentProcessId, CommandLine, ExecutablePath | Where-Object {$_.CommandLine -ne $null} | Sort-Object Name | Format-List
```

**Note:** WMI cmd line access may be restricted for other users' processes at T1.

**Flag:**
- `powershell.exe` with `-EncodedCommand`, `-enc`, `-e ` - encoded command execution
- `powershell.exe` with `-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass` - stealth execution
- `cmd.exe /c` followed by long base64-like strings
- `wscript.exe`/`cscript.exe` with scripts from `%TEMP%` or `%APPDATA%`
- `rundll32.exe` with unusual DLL paths (not `System32`)
- `regsvr32.exe /s /u /i:http://...` - Squiblydoo technique
- `mshta.exe` with URL argument - HTML App execution
- Office apps (`WINWORD.EXE`, `EXCEL.EXE`) spawning `cmd.exe`, `powershell.exe`, `wscript.exe` - macro exploitation

---

### 1.3 - Processes Running from Suspicious Locations
**Tier:** T1  

```powershell
# Processes from %TEMP%
Get-Process | Where-Object {$_.Path -like "*\Temp\*" -or $_.Path -like "*\AppData\Local\Temp\*"} | Select-Object Name, Id, Path | Format-Table -AutoSize

# Processes from %APPDATA%
Get-Process | Where-Object {$_.Path -like "*\AppData\Roaming\*" -and $_.Path -notlike "*\Microsoft\*"} | Select-Object Name, Id, Path | Format-Table -AutoSize

# Processes from Downloads folder
Get-Process | Where-Object {$_.Path -like "*\Downloads\*"} | Select-Object Name, Id, Path | Format-Table -AutoSize
```

---

### 1.4 - Authenticode Signature Verification for Running Processes
**Tier:** T1  

```powershell
Get-Process | Where-Object {$_.Path} | ForEach-Object {
    $sig = Get-AuthenticodeSignature $_.Path -ErrorAction SilentlyContinue
    if ($sig.Status -ne 'Valid') {
        [PSCustomObject]@{
            Name   = $_.Name
            PID    = $_.Id
            Path   = $_.Path
            Status = $sig.Status
        }
    }
} | Format-Table -AutoSize
```

**Flag:**
- `NotSigned` - no digital signature
- `HashMismatch` - binary tampered (critical)
- `UnknownError` - cannot verify (investigate)
- `NotTrusted` - signed but not by trusted authority

---

### 1.5 - Parent Process Anomalies
**Tier:** T1  

```powershell
$procs = Get-WmiObject Win32_Process | Group-Object ProcessId -AsHashTable -AsString
Get-WmiObject Win32_Process | Where-Object {$_.Name -in @('powershell.exe','cmd.exe','wscript.exe','cscript.exe','mshta.exe')} | ForEach-Object {
    $parent = $procs[$_.ParentProcessId.ToString()]
    [PSCustomObject]@{
        Child      = $_.Name
        ChildPID   = $_.ProcessId
        Parent     = if($parent){$parent.Name}else{"[DEAD/UNKNOWN]"}
        ParentPID  = $_.ParentProcessId
        CommandLine = $_.CommandLine
    }
} | Format-Table -AutoSize
```

**Suspicious parent → child pairs:**
- `WINWORD.EXE` / `EXCEL.EXE` / `OUTLOOK.EXE` → `powershell.exe`, `cmd.exe`, `wscript.exe`
- `explorer.exe` → `powershell.exe` with long/encoded cmdline
- `svchost.exe` → `cmd.exe` / `powershell.exe` (unusual - svchost doesn't spawn shells)
- `chrome.exe` / `firefox.exe` → `cmd.exe` / `powershell.exe` (browser exploitation)
- Any process → `[DEAD/UNKNOWN]` parent (orphaned - parent was dropper that exited)

---

## Phase 2: Network Activity


---

### 2.1 - Listening Ports
**Tier:** T1  

```powershell
Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess | Sort-Object LocalPort | ForEach-Object {
    $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        LocalAddress = $_.LocalAddress
        LocalPort    = $_.LocalPort
        PID          = $_.OwningProcess
        ProcessName  = $proc.Name
        ProcessPath  = $proc.Path
    }
} | Format-Table -AutoSize
```

---

### 2.2 - Established Outbound Connections
**Tier:** T1  

```powershell
Get-NetTCPConnection -State Established | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess | ForEach-Object {
    $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        LocalPort    = $_.LocalPort
        RemoteAddr   = $_.RemoteAddress
        RemotePort   = $_.RemotePort
        PID          = $_.OwningProcess
        ProcessName  = $proc.Name
        ProcessPath  = $proc.Path
    }
} | Format-Table -AutoSize
```

**Flag:**
- Connections from `powershell.exe`, `cmd.exe`, `wscript.exe` to external IPs
- Connections to unusual ports (not 80/443/53) to external IPs
- RFC1918 connections from unusual processes - lateral movement
- Multiple connections from same process to different external IPs - C2 rotation

---

### 2.3 - DNS Cache
**Tier:** T1  

```powershell
Get-DnsClientCache | Select-Object Entry, RecordName, RecordType, Status, TimeToLive, DataLength, Section, Data | Format-Table -AutoSize

# Alternative (cmd-based)
ipconfig /displaydns | Select-String "Record Name|Data"
```

**Flag:**
- DGA-like domain names (random strings, e.g., `asdkfj1234.top`, `qxzrp.club`)
- Unusual TLDs: `.top`, `.xyz`, `.tk`, `.pw`, `.cc` - malware C2 favorites
- Recently resolved domains at unusual hours
- Domains that look like IPs but aren't (obfuscation)

---

### 2.4 - HOSTS File
**Tier:** T1  

```powershell
Get-Content C:\Windows\System32\drivers\etc\hosts | Where-Object {$_ -notmatch "^#" -and $_ -ne ""}
```

---

## Phase 3: Persistence Mechanisms


---

### 3.1 - Registry Run Keys
**Tier:** T1  

```powershell
# Per-user Run (current user, runs on login)
Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Run -ErrorAction SilentlyContinue

# Per-user RunOnce
Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce -ErrorAction SilentlyContinue

# System-wide Run (all users, requires access)
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Run -ErrorAction SilentlyContinue

# System-wide RunOnce
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce -ErrorAction SilentlyContinue

# 32-bit Run keys (on 64-bit systems)
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
Get-ItemProperty "HKCU:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
```

**Flag:**
- Values pointing to `%TEMP%`, `%APPDATA%`, `%LOCALAPPDATA%`, `C:\Users\*\Downloads`
- Inline PS: `powershell.exe -enc ...`
- Script files (`.vbs`, `.js`, `.ps1`, `.bat`) in unusual locations
- Random-looking names or values
- Check registry key mtime for recency

---

### 3.2 - Winlogon and BootExecute
**Tier:** T1  

```powershell
# Winlogon - should only have specific trusted values
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" | Select-Object Shell, Userinit, Taskman, VMApplet

# Boot execute - runs before logon
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager" | Select-Object BootExecute

# AppInit DLLs (DLL injection on every process)
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" | Select-Object AppInit_DLLs, LoadAppInit_DLLs
```

**Expected values:**
- `Shell`: `explorer.exe` ONLY - any additional entries = suspicious
- `Userinit`: `C:\Windows\system32\userinit.exe,` (trailing comma normal)
- `BootExecute`: `autocheck autochk *` ONLY - additional entries = suspicious
- `AppInit_DLLs`: empty or `0` for `LoadAppInit_DLLs`

**Flag immediately:**
- Any additional `Shell` values beyond `explorer.exe`
- `BootExecute` with entries beyond `autocheck`
- Any `AppInit_DLLs` DLL - injects into every user-mode process

---

### 3.3 - Startup Folders
**Tier:** T1  

```powershell
# Current user startup
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" -ErrorAction SilentlyContinue | Select-Object Name, LastWriteTime, FullName

# All users startup
Get-ChildItem "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" -ErrorAction SilentlyContinue | Select-Object Name, LastWriteTime, FullName
```

**Flag:**
- LNK files pointing to unusual scripts or executables
- `.vbs`, `.js`, `.ps1`, `.bat` in startup folder
- Recently added items (check `LastWriteTime`)

---

### 3.4 - Scheduled Tasks
**Tier:** T1  

```powershell
# All non-disabled tasks
Get-ScheduledTask | Where-Object {$_.State -ne 'Disabled'} | Select-Object TaskName, TaskPath, State, Description | Sort-Object TaskPath | Format-Table -AutoSize

# Get action details for each task (what it actually runs)
Get-ScheduledTask | Where-Object {$_.State -ne 'Disabled'} | ForEach-Object {
    $actions = $_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }
    [PSCustomObject]@{
        Name     = $_.TaskName
        Path     = $_.TaskPath
        RunAs    = $_.Principal.UserId
        Action   = $actions -join "; "
    }
} | Where-Object {$_.Action -match "%TEMP%|%APPDATA%|powershell|wscript|cscript|mshta|\\Users\\.*\\AppData\\Local"} | Format-List
```

**Flag:**
- Tasks with `Execute` pointing to `%TEMP%`, `%APPDATA%`, or user profile dirs
- Tasks using `powershell.exe -enc`, `wscript.exe`, `mshta.exe`
- Tasks in `\Microsoft\Windows\` paths not matching known Windows components
- Recently created tasks (sort by creation, or Event 4698 in Security log)
- `SYSTEM`-running tasks with scripts from non-System32 paths

---

### 3.5 - Running Services with Full Paths
**Tier:** T1  

```powershell
# All running services with their binary paths
Get-WmiObject Win32_Service | Where-Object {$_.State -eq 'Running'} | Select-Object Name, DisplayName, PathName, StartName, StartMode | Sort-Object Name | Format-Table -AutoSize

# Flag unusual service paths
Get-WmiObject Win32_Service | Where-Object {
    $_.State -eq 'Running' -and
    ($_.PathName -like "*\Temp\*" -or $_.PathName -like "*\AppData\*" -or $_.PathName -like "*\Users\*")
} | Select-Object Name, PathName, StartName | Format-List
```

**Flag:**
- `PathName` in `%TEMP%`, `%APPDATA%`, or user profile dirs
- `LocalSystem` (`NT AUTHORITY\SYSTEM`) services with suspicious paths
- Services with no `DisplayName` or random-looking names
- Services not associated with any installed product

---

### 3.6 - WMI Event Subscriptions (Critical - High Fidelity IOC)
**Tier:** T1 / T2  

```powershell
# Event Filters (trigger conditions)
Get-WmiObject -Namespace root\subscription -Class __EventFilter -ErrorAction SilentlyContinue | Select-Object Name, Query, QueryLanguage | Format-List

# Event Consumers (what to do when triggered)
Get-WmiObject -Namespace root\subscription -Class __EventConsumer -ErrorAction SilentlyContinue | Select-Object Name, CommandLineTemplate, ScriptText, ScriptingEngine | Format-List

# Bindings (connects filter to consumer)
Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding -ErrorAction SilentlyContinue | Select-Object Filter, Consumer | Format-List
```

**Flag:**
- **ANY non-Microsoft WMI subscriptions** - rarely legit software, favorite APT persistence
- `CommandLineConsumer` with `CommandLineTemplate` running PS, cmd, or scripts
- `ActiveScriptEventConsumer` with inline VBScript/JScript (`ScriptText` = payload)
- Bindings connecting timing/system event filter to command execution consumer

---

## Phase 4: File Activity


---

### 4.1 - Executable Files in Temp Locations
**Tier:** T1  

```powershell
# Executables/scripts in %TEMP%
Get-ChildItem $env:TEMP -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.Extension -in @('.exe','.dll','.ps1','.bat','.vbs','.js','.hta','.scr','.com','.pif')} | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize

# %APPDATA% executables (should rarely have .exe here)
Get-ChildItem $env:APPDATA -Recurse -Depth 3 -ErrorAction SilentlyContinue | Where-Object {$_.Extension -eq '.exe'} | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize

# %LOCALAPPDATA% executables outside of expected app paths
Get-ChildItem $env:LOCALAPPDATA -Recurse -Depth 2 -ErrorAction SilentlyContinue | Where-Object {$_.Extension -eq '.exe' -and $_.FullName -notmatch 'Microsoft|Google|Mozilla|Programs'} | Select-Object FullName, LastWriteTime | Format-Table -AutoSize
```

---

### 4.2 - Authenticode Verification for Suspicious Files
**Tier:** T1  

```powershell
# Check authenticode signature for a specific file
Get-AuthenticodeSignature "C:\path\to\suspicious\file.exe" | Select-Object Path, Status, SignerCertificate | Format-List

# Batch check temp directory
Get-ChildItem $env:TEMP -Filter *.exe -ErrorAction SilentlyContinue | ForEach-Object {
    $sig = Get-AuthenticodeSignature $_.FullName -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        File   = $_.Name
        Status = $sig.Status
        Signer = $sig.SignerCertificate.Subject
    }
} | Format-Table -AutoSize
```

---

### 4.3 - VBScript/JScript/HTA Artifacts
**Tier:** T1  

```powershell
# Script artifacts in temp and user dirs
Get-ChildItem $env:TEMP -ErrorAction SilentlyContinue | Where-Object {$_.Extension -in @('.vbs','.js','.hta','.wsf','.wsh')} | Select-Object FullName, LastWriteTime
Get-ChildItem $env:APPDATA -Depth 2 -ErrorAction SilentlyContinue | Where-Object {$_.Extension -in @('.vbs','.js','.hta')} | Select-Object FullName, LastWriteTime
```

---

## Phase 5: User & Account Activity


---

### 5.1 - Local User Accounts
**Tier:** T1  

```powershell
Get-LocalUser | Select-Object Name, Enabled, LastLogon, PasswordLastSet, PasswordRequired, Description | Format-Table -AutoSize
```

**Flag:**
- Enabled accounts you don't recognize
- `PasswordLastSet` recently changed - especially for Administrator/admin
- `LastLogon` for accounts that shouldn't log in
- Guest account enabled - should be disabled on managed systems
- `PasswordRequired = False` on accounts that should require passwords

---

### 5.2 - Local Administrators Group
**Tier:** T1  

```powershell
Get-LocalGroupMember -Group Administrators -ErrorAction SilentlyContinue | Format-Table -AutoSize

# cmd fallback
net localgroup administrators
```

**Flag:**
- Unrecognized accounts in Administrators group
- Domain accounts in local Administrators that shouldn't be

---

### 5.3 - T2: Windows Security Event Log - Authentication Events
**Tier:** T2 (admin access to Security log)  

```powershell
# Successful logins (4624), failed logins (4625), account created (4720), account deleted (4726), account changed (4738)
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4624 or EventID=4625 or EventID=4720 or EventID=4726 or EventID=4738]]" -MaxEvents 200 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, @{n='Message';e={$_.Message -replace '\s+',' '}} | Format-Table TimeCreated, Id -AutoSize

# Interactive logons only (LogonType=2 or 10=RemoteInteractive)
Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4624]][EventData[Data[@Name='LogonType']='2' or Data[@Name='LogonType']='10']]" -MaxEvents 50 -ErrorAction SilentlyContinue | Format-List TimeCreated, Message
```

**Flag:**
- **4625** (Failed login) rapid succession same source - brute force
- **4624** LogonType **3** (Network) from unusual IPs or accounts
- **4624** LogonType **10** (RDP) - who is RDPing in?
- **4720** (Account Created) - new account?
- **4726** (Account Deleted) - covering tracks?

---

## Phase 6: Driver Activity


---

### 6.1 - T2: Driver Query
**Tier:** T2 (admin recommended for full output)  

```powershell
# Running drivers with paths
driverquery /v /fo CSV 2>$null | ConvertFrom-Csv | Where-Object {$_.'State' -eq 'Running'} | Select-Object 'Module Name','Display Name','Driver Type','Start Mode','Path' | Format-Table -AutoSize

# Check signature status of drivers (can take a few minutes)
Get-WmiObject Win32_SystemDriver | Where-Object {$_.State -eq 'Running'} | ForEach-Object {
    $name = $_.Name
    $path = $_.PathName
    $sig = Get-AuthenticodeSignature $path -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        Name   = $name
        Status = $sig.Status
        Signer = $sig.SignerCertificate.Subject
        Path   = $path
    }
} | Where-Object {$_.Status -ne 'Valid'} | Format-Table -AutoSize
```

**Flag:**
- Drivers with `NotSigned` or `HashMismatch`
- Drivers loading from `C:\Users\*`, `%TEMP%`, or non-standard paths
- Generic or suspicious driver names not associated with known hardware/software

---

### 6.2 - T2: Named Pipes (C2 Framework Indicator)
**Tier:** T2  

```powershell
# List all named pipes
[System.IO.Directory]::GetFiles('\\.\pipe\') | Sort-Object

# PowerShell alternative
Get-ChildItem \\.\pipe\ -ErrorAction SilentlyContinue | Select-Object Name | Sort-Object Name
```

**Known malicious pipe names (Cobalt Strike + C2 defaults):**
- `msagent_*` - CS SMB beacon
- `MSSE-*-server` - CS
- `postex_*` - CS
- `status_*` - CS
- `mypipe-*` - various C2
- `\\.\.pipe\isapi_http` - CS
- `\\.\.pipe\isapi_dg` - CS

**Flag:**
- Any of above pipe patterns
- Pipes with random hex names
- Pipes from unexpected processes (find which process owns)

---

## Phase 7: Script & Command Execution


---

### 7.1 - PowerShell Command History
**Tier:** T1  

```powershell
# PSReadLine history (most complete)
$histPath = (Get-PSReadlineOption).HistorySavePath
if (Test-Path $histPath) { Get-Content $histPath | Select-Object -Last 150 }

# Check for encoded commands
if (Test-Path $histPath) {
    Get-Content $histPath | Select-String -Pattern "encodedcommand|-enc |-e [A-Za-z]|downloadstring|downloadfile|iex|invoke-expression|bypass|hidden|noprofile" -CaseSensitive:$false
}
```

**Flag:**
- `-EncodedCommand` or `-enc` with base64 payload
- `IEX`/`Invoke-Expression` downloading + executing remote content
- `DownloadString(` or `DownloadFile` with external URLs
- `-ExecutionPolicy Bypass -WindowStyle Hidden -NonInteractive` - stealth execution
- `Set-MpPreference -DisableRealtimeMonitoring` - Defender disable
- `Add-MpPreference -ExclusionPath` - Defender exclusion (malware hiding itself)
- `certutil -decode` - base64 payload decode
- `regsvr32 /s /u /i:` - Squiblydoo AppLocker bypass

---

### 7.2 - T2: PowerShell Script Block Logging (Event 4104)
**Tier:** T2 (requires Script Block Logging to be enabled via GPO)  

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 200 -ErrorAction SilentlyContinue | Where-Object {$_.Id -eq 4104} | Select-Object TimeCreated, @{n='Script';e={$_.Message}} | Format-List
```

**Note:** Requires Script Block Logging configured (`...PowerShell\ScriptBlockLogging` → `EnableScriptBlockLogging = 1`). No output if not configured.

---

### 7.3 - PowerShell Transcription Logs
**Tier:** T1  

```powershell
# Common transcription log locations
Get-ChildItem "$env:SystemRoot\Transcripts" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName, LastWriteTime | Sort-Object LastWriteTime -Descending
Get-ChildItem "$env:USERPROFILE\Documents\PowerShell_transcript*" -ErrorAction SilentlyContinue
```

---

### 7.4 - BITS Transfer Jobs
**Tier:** T1  

```powershell
# All BITS jobs (including other users if admin)
Get-BitsTransfer -AllUsers -ErrorAction SilentlyContinue | Select-Object DisplayName, TransferType, JobState, BytesTransferred, BytesTotal, CreationTime, RemoteUrl, LocalName | Format-List

# Legacy cmd
bitsadmin /list /alljobs 2>$null
```

**Flag:**
- BITS jobs with `RemoteUrl` to unusual external URLs
- Jobs in `Suspended` or `Transferred` state - completed download
- Jobs downloading to `%TEMP%` or user profile dirs
- BITS jobs from unusual processes (check `OwnerAccount`)

---

## Phase 8: EDR/Security Tool Status


---

### 8.1 - Windows Defender Status
**Tier:** T1  

```powershell
# Defender status
Get-MpComputerStatus -ErrorAction SilentlyContinue | Select-Object AMRunningMode, AntivirusEnabled, RealTimeProtectionEnabled, IoavProtectionEnabled, AntispywareEnabled, BehaviorMonitorEnabled, OnAccessProtectionEnabled, LastQuickScanEndTime, LastFullScanEndTime

# Recent threat detections
Get-MpThreatDetection -ErrorAction SilentlyContinue | Select-Object -First 20 | Select-Object ActionSuccess, CurrentThreatExecutionStatusID, DetectionID, InitialDetectionTime, ThreatName | Format-Table -AutoSize
```

**Flag:**
- `RealTimeProtectionEnabled = False` - real-time protection disabled
- `AntivirusEnabled = False` - AV disabled
- `AMRunningMode = NotRunning` - Defender not running
- Recent threat detections (last 24-48h) requiring investigation
- Last scan times very old (no recent scans)

---

### 8.2 - Third-Party EDR Agent Processes
**Tier:** T1  

```powershell
# Check for common EDR agents
Get-Process -ErrorAction SilentlyContinue | Where-Object {$_.Name -match "falcon|sentinel|elastic|mdatp|MsSense|cbagentd|cylance|eset|sophos|malwarebytes|carbon|osquery|wazuh|ossec|cybereason"} | Select-Object Name, Id, Path, Company | Format-Table -AutoSize
```

---

### 8.3 - T2: Security Audit Policy
**Tier:** T2 (admin required)  

```powershell
# Check what's being audited
auditpol /get /category:* 2>$null

# Check if process creation command line is being captured
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" -ErrorAction SilentlyContinue | Select-Object ProcessCreationIncludeCmdLine_Enabled
```

**Flag:**
- `Process Creation` not audited - Event 4688 not logging process starts
- `Logon/Logoff` not audited - no auth logging
- `Object Access` not audited - no file/registry access logging
- `ProcessCreationIncludeCmdLine_Enabled = 0` or missing - cmdlines not captured in 4688

---

## Quick Reference: Windows IOC Severity Ratings

| IOC | Severity | Notes |
|-----|----------|-------|
| WMI event subscription exists (non-Microsoft) | Critical | APT-grade persistence technique - almost never legitimate |
| Named pipe matching Cobalt Strike defaults | Critical | Active C2 framework indicator |
| `powershell.exe -enc` with base64 payload | Critical | Encoded command execution - very suspicious |
| Process running from `%TEMP%` | Critical | Almost never legitimate executable |
| `AppInit_DLLs` set to any non-empty value | Critical | DLL injection into every process |
| `Winlogon\Shell` != `explorer.exe` only | Critical | Shell replacement - likely rootkit |
| Registry Run key pointing to `%TEMP%`/`%APPDATA%` | High | Persistent malware |
| Service with binary in user profile directory | High | Malware as service |
| Office app spawning PowerShell | High | Macro exploitation |
| `Get-MpComputerStatus` shows AV disabled | High | Defender killed/tampered with |
| Scheduled task running from `%APPDATA%` | High | Persistence mechanism |
| `HashMismatch` on running executable | Critical | Binary has been patched/backdoored |
| BITS transfer job to unknown URL | Medium | Stealthy download channel |
| Unsigned driver loaded | High | Potential kernel rootkit |
| `mshta.exe` with URL argument | High | HTML Application execution - LOLBin abuse |
| Guest account enabled | Medium | Reduces security posture |
