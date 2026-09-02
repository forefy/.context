# Known Targeted Attacks - macOS

> Concise pointers to named campaigns targeting macOS. Match hunt output against these high-signal IOCs.
> **These rotate.** Hashes/domains go stale fast; LaunchDaemon labels, dropped filenames, and behavioral patterns are more durable. Always confirm against the linked source before calling a `❌ FAIL`.

| Campaign (aliases) | Type | High-signal IOCs (defanged) | Source |
|---|---|---|---|
| **Atomic macOS Stealer** (AMOS) | Infostealer + persistent backdoor, via cracked apps, fake installer `.dmg`, and `curl \| bash` terminal lures | **Persistence (LaunchDaemon):** `/Library/LaunchDaemons/com.finder.helper.plist` → runs `.agent` via `/bin/bash` at boot<br>**Hidden drop files (home dir):** `~/.helper` (main binary), `~/.agent` (loop script), `~/.pass` (captured password), `~/.username`<br>**Behavior:** `osascript` fake "System Preferences/System Settings" password dialog; Keychain export; browser cred harvest (Chrome/Firefox/Safari/Edge/Brave/Opera/Vivaldi); staged as `/tmp/out.zip`; crypto-wallet targeting<br>**Delivery filenames:** `Installer_v.X.XX.dmg` (e.g. `v.2.13`, `v.3.89`, `v.7.26`)<br>**C2 / landing:** `ekochist[.]com`, `misshon[.]com`, `toutentris[.]com`; install scripts `goatramz[.]com/get4/install.sh`, `letrucvert[.]com/get8/install.sh`; exfil `sivvino[.]com/contact`, `45[.]94[.]47[.]149`, `45[.]94[.]47[.]186`<br>**Detections:** `Trojan.MacOS.Amos.PFH`, `TrojanSpy.MacOS.AMOS.MANP`<br>**Variant - masquerades as Apple daemons (Objective-See):** LaunchAgents `com.apple.systemupdate` / `com.apple.mdworker` (`~/Library/LaunchAgents/com.apple.mdworker.plist`); drops `~/.pwd`, `~/.marker`, `/tmp/helper`, `/tmp/archive.tar.gz`; C2 `laislivon[.]com`, `rvdownloads[.]com/frozenfix/update`; 256 hardcoded wallet-extension IDs (e.g. MetaMask `nkbihfbeogaeaoehlefnkodbefgpgknn`)<br>_Persistence label/path varies per build (`com.finder.helper` vs. Apple-masquerading names) - match on any._ | [Trend Micro, 2025-09](https://www.trendmicro.com/en_us/research/25/i/an-mdr-analysis-of-the-amos-stealer-campaign.html) · [Objective-See, 2026-04](https://objective-see.org/blog/blog_0x88.html) |

<!--
Add a row per campaign. Keep IOC cells to the most distinctive, low-false-positive indicators
(LaunchDaemon/LaunchAgent labels, dropped filenames, osascript behavior) - link the source for the full list.
-->
