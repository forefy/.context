# Known Targeted Attacks - Windows

> Concise pointers to named campaigns targeting Windows. Match hunt output against these high-signal IOCs.
> **These rotate.** Hashes/IPs/domains go stale fast; scheduled-task names, registry keys, and drop-path patterns are more durable. Always confirm against the linked source before calling a `❌ FAIL`.

| Campaign (aliases) | Type | High-signal IOCs (defanged) | Source |
|---|---|---|---|
| **Silver Fox** (Yinhu / 银狐) | Counterfeit-installer → RAT, via SEO-poisoned fake software download sites | **Scheduled tasks (very distinctive):** `\Deadline Mission Target`, `\Hierarchy Tools Smooth Inventory`, `\Empowering Status Tools productivity Ahead`, `\5nboF`<br>**Defense tamper (registry):** path added to `HKLM\SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths`; Windows Update disabled via `HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate\AU` + tampered `WaaSMedicSvc`/`wuauserv`/`UsoSvc`<br>**Dropper filenames:** `ainst*.exe`, `a_instapp*.exe`, `ainstaller-*.exe`, `zinst*`, `intsoft*`, `innstll*`, `XPSPLOG.dll`<br>**Drop paths:** `C:\Users\Public\<rand>\<rand>.exe`, `C:\ProgramData\<rand>\<rand>.exe`<br>**Loader:** TrueUpdate<br>**C2 domains:** `iualef[.]net`, `oijfwe[.]net`, `euioxu[.]net`, `czijbh[.]net`, `wfmwsj[.]net`, `tbdqxq[.]net` (ports 5090 / 7031 / 8050 / 28300)<br>**Lure typosquats:** `pc-razerzone[.]com[.]cn`, `app-microsoft-edge[.]com[.]cn`, `kaspersky-lab[.]hl[.]cn`, `baidu-pan[.]com[.]cn` (many `*.com.cn` / `*.hl.cn`) | [Microsoft, 2026-09-01](https://www.microsoft.com/en-us/security/blog/2026/09/01/counterfeit-installers-system-compromise-tracking-deceptive-software-download-campaign/) |

| **The Gentlemen** (TukTuk C2 framework) | Human-operated ransomware; BYOVD EDR-killer + DLL sideloading | **BYOVD drivers:** `eb.sys` (GentleKiller variant, SHA256 `97BD65E9…3B1BE091`), `wsftprm.sys`<br>**Loader / C2 agent:** `TukTuk.exe` (SHA256 `e2b31ac7…78f01f9`), delivered in `tuktuk-v2.0_10.zip`<br>**DLL sideload:** legit `Greenshot.exe` side-loads malicious `log4net.dll` (SHA256 `096ec378…42d6c584`)<br>**EDR-kill binaries:** `EDRKiller`, `WarsawKiller`, `UnknownKiller.exe`<br>**C2:** `borjumaniya[.]store`, `65[.]109[.]70[.]162` (Hetzner FI)<br>**Operator artifacts:** operator id "Neo", build host `DESKTOP-22EVPBQ` | [Oasis Security, 2026-08-31](https://oasis-security.io/blog/The-Gentlemen-Ransomware-Hacker-Groups-TukTuk-Framework) |

<!--
Add a row per campaign. Keep IOC cells to the most distinctive, low-false-positive indicators
(task names, registry keys, service names, filename patterns) - link the source for the full list.
-->
