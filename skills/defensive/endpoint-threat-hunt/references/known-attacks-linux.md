# Known Targeted Attacks - Linux

> Concise pointers to named campaigns targeting Linux. Match hunt output against these high-signal IOCs.
> **These rotate.** Hashes/IPs/domains go stale fast; package versions, process names, and file paths are more durable. Always confirm against the linked source before calling a `❌ FAIL`.

| Campaign (aliases) | Type | High-signal IOCs (defanged) | Source |
|---|---|---|---|
| **XZ Utils backdoor** (CVE-2024-3094) | Supply-chain backdoor in `liblzma`, hooks OpenSSH auth via systemd | **Affected versions:** XZ Utils / `liblzma` **5.6.0** and **5.6.1** (`xz --version`, `rpm -q xz` / `dpkg -l liblzma5`)<br>**Build artifact:** malicious `build-to-host.m4` present only in the tarball release (not in Git)<br>**Mechanism:** modified OpenSSH function reached through the systemd interface on `x86-64` glibc/GCC builds (`dpkg`/`rpm`)<br>**Affected distros:** Fedora, Debian (sid), Ubuntu, openSUSE, Red Hat rolling/testing branches<br>**Attacker persona:** committer "Jia Tan" (sock puppets "Jigar Kumar", "krygorin4545", "misoeater91") | [Wikipedia / CVE-2024-3094](https://en.wikipedia.org/wiki/XZ_Utils_backdoor) |

| **The Gentlemen** (TukTuk C2 framework) | Cross-platform C2 agent (paired with a Windows ransomware toolkit) | **Linux agent:** TukTuk agent retrieves commands via a `poll()` loop (delivered in `tuktuk-v2.0_10.zip`, SHA256 `e7408841…681f9923`)<br>**Shared C2 infra (pivot from either OS):** `borjumaniya[.]store`, `65[.]109[.]70[.]162` (Hetzner FI)<br>_Fewer host-file IOCs published for the Linux agent than Windows - hunt on the shared C2 and the agent process._ | [Oasis Security, 2026-08-31](https://oasis-security.io/blog/The-Gentlemen-Ransomware-Hacker-Groups-TukTuk-Framework) |

<!--
Add a row per campaign. Keep IOC cells to the most distinctive, low-false-positive indicators
(package versions, process/module names, drop paths, systemd ExecStart) - link the source for the full list.
-->
