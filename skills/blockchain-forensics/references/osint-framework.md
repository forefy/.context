# OSINT Framework

Use OSINT to bridge the gap between pseudonymous wallet addresses and real-world actors.

## 6.1 Principle: OSINT + On-Chain = Attribution

Blockchain data proves what happened. OSINT reveals who made it happen. Neither is sufficient alone — triangulate both.

**Rule:** One OSINT signal is a lead. Three corroborating signals from independent sources = attribution hypothesis. Five+ with on-chain confirmation = strong attribution case.

## 6.2 OSINT Sources (Free-First)

**Social Media (free):**
- **Twitter/X search** — search the attacker address in quotes. Often surfaces prior mentions, scam promotions, or community reports.
  > Instruction: `Go to x.com → search "0xABCD...1234" (with quotes) → filter by Latest → look for any prior mentions, scam campaigns, or investigator threads linking this address.`
- **Telegram** — many drainer services advertise openly. Search address in Telegram search bar.
- **Reddit** — r/CryptoScams, r/ethereum frequently have victim reports with attacker addresses
- **YouTube/TikTok** — scam promotions often embed deposit addresses in video descriptions
- **Perplexity / AI-powered search** — use as a first-pass discovery sweep to surface mentions of wallet addresses, usernames, or scam campaigns across publicly indexed data. Faster than manual search, but never treat results as verified.
  > Instruction: `Ask Perplexity: "Has wallet 0xABCD... appeared in any scam reports, security research, or Telegram channels?" Cross-verify every hit on-chain before using it.`

**Domain / Infrastructure (free tools):**
- **WHOIS** (`who.is`) — check domain registration date, hosting provider, registrar email. Scam sites often registered same day as the campaign.
- **urlscan.io** — scan any suspicious URL. See JavaScript, embedded addresses, linked domains, and screenshots even after takedown.
  > Instruction: `Go to urlscan.io → paste the suspicious URL → run scan → look under "Indicators" for any wallet addresses embedded in the page source.`
- **Wayback Machine** (`web.archive.org`) — capture snapshots of phishing sites before they go down.
- **SecurityTrails** (`securitytrails.com`, free tier) — DNS history, subdomain enumeration, IP history.
- **SSL certificate search** (`crt.sh`) — find all domains sharing the same SSL certificate. Attackers often reuse certificates across scam sites.
  > Instruction: `Go to crt.sh → search the domain → expand the certificate → copy the Common Name → search again to find all sibling domains using the same certificate.`
- **Site Sentry** (Telegram bot) — monitors phishing site front-end changes and infrastructure updates in real time. Alerts when known scam domains update or switch infrastructure — useful for tracking active campaigns.
  > Instruction: `Search Telegram for "Site Sentry" bot → submit domains you're monitoring → receive alerts when the front end or hosting changes.`

**Developer Repositories (free):**
- **GitHub** — search the attacker address or deployer address on GitHub. Attackers often commit test addresses or API keys inadvertently.
  > Instruction: `Go to github.com → use the search bar → enter the wallet address in quotes → filter by "Code" → look for any repository referencing this address.`
- **DPRK / threat actor repositories** — look at repositories confirmed as belonging to nation-state actors or cybercrime groups. They often reveal: repeated coding styles, reused infrastructure, and multiple aliases managed by the same actor. Code commits, usernames, and email addresses can unmask clusters of fake identities.
  > Instruction: `Search GitHub for the attacker's known username or any identifier from the on-chain investigation. Compare commit history, coding patterns, and linked accounts across multiple repos.`
- **Bitcointalk** — early project announcements, presale addresses. Forum posts are indexed and searchable.
- **Medium/Substack** — fraudulent project "official guides" often embed collection addresses.

**Exchange Announcements and Threat Feeds (free):**
- **Chainabuse** (`chainabuse.com`) — crowdsourced scam reports indexed by address
- **ScamSniffer** (`scamsniffer.io`) — drainer and phishing campaign database
- **CryptoScamDB** — aggregated scam address database
- **CoinHolmes** — public reporting platform aggregating community-reported scam addresses and incident reports
- **SEAL-ISAC** — both a structured threat intelligence sharing network (apply for access) AND a public reporting platform for extortion, scam addresses, and crypto-native security incidents; check it for address lookups alongside Chainabuse
- **OFAC SDN List** (`home.treasury.gov/...`) — check if address is sanctioned
  > Instruction: `Go to home.treasury.gov → search "SDN List" → download CSV or use web search → search the address. Or use sanctioned.us for faster lookup.`
- **MistTrack** (`misttrack.io`, free basic search) — risk scoring and address tagging

**Legal & Regulatory Documents (free, highest credibility):**
- **OFAC/Treasury sanctions notices** — contain previously unknown wallet addresses and entity aliases at the moment of sanctioning. Download the full SDN CSV to search locally.
  > Instruction: `Go to home.treasury.gov/policy-issues/financial-sanctions/specially-designated-nationals-and-blocked-persons-list-sdn-human-readable-lists → download CSV → search the file for wallet addresses or entity names related to your case.`
- **DOJ indictments and court filings** — criminal indictments (particularly against exchange operators, mixer services, and DPRK actors) often list specific wallet addresses, transaction hashes, and entity infrastructure. Free via PACER (US federal courts) or news coverage.
- **Europol/Eurojust press releases** — coordinate cross-border seizures and name wallets/exchanges involved. Free via Europol's newsroom.
- **UN Security Council Panel reports on DPRK** — contain attribution analysis, wallet clusters, and on-chain evidence used in sanctions proceedings. Published annually with specific blockchain evidence.
- **Reuters, CoinDesk, The Block** — major hacks are covered within hours; reporters cite official exchange/regulator disclosures that may include attacker wallet addresses not yet on community threat feeds. Treat as secondary confirmation, then validate on-chain.
  > Instruction: `Search: "site:reuters.com OR site:coindesk.com OR site:theblock.co 0xATTACKERWALLET" to surface any journalist-published references to the address.`
- **Academic papers and research datasets** — universities and research groups publish structured datasets on darknet wallets, mixing typologies, and laundering case studies. Search Google Scholar for the blockchain/technique in question. Useful for validating heuristics and understanding emerging methods.

**File & Image Metadata (free, often overlooked):**
- PDFs, whitepapers, images, and documents shared by threat actors often retain **EXIF data, creation timestamps, and software version tags**
- These can reveal: creator's time zone (created/modified timestamps), operating system, application version, device fingerprints
- Practical use: if a scammer shares a "whitepaper", token deck, or screenshot — extract metadata before discarding it as evidence
  > Instruction: `On Mac/Linux: run \`exiftool filename.pdf\` (install with \`brew install exiftool\` or \`apt install libimage-exiftool-perl\`). Look at "Create Date", "Modify Date", "Creator Tool", "Author", and "GPS" fields. Timestamps reveal likely timezone of the creator. Cross-reference with on-chain transaction timestamps for correlation.`
  > Instruction: `For images: upload to \`jimpl.com\` (free web EXIF viewer) if you don't have exiftool. Note: many platforms strip EXIF on upload — the most useful metadata comes from files shared via Telegram or email, not re-uploaded images.`

**Stablecoin Blacklists (free, on-chain):**
- USDT (Ethereum): Call `isBlacklisted(address)` on USDT contract (`0xdAC17F...`)
- USDC (Ethereum): Call `isBlacklisted(address)` on USDC contract (`0xA0b86...`)
  > Instruction: `Go to etherscan.io → search USDT contract address → "Read Contract" → find isBlacklisted → enter the attacker's address → Execute.`

**Leaked Databases (use with OPSEC):**
- **Have I Been Pwned** (`haveibeenpwned.com`) — free. Check if associated email appeared in a breach.
- **Intelligence X** (`intelx.io`, limited free tier) — indexes paste dumps, darknet, and leaked data.
- **BreachForums / successor marketplaces** — known hubs where breach data, stolen accounts, and crypto cashout services are traded. Wallet addresses and stolen CEX credentials appear here. ⚠️ Use extreme caution: legal gray area; use isolated VM + Tor + no personal accounts; treat findings as leads requiring on-chain corroboration, never as proof.

**Paid OSINT tools (recommend if institutional context):**
- Dehashed — email/username/IP/domain cross-search across breach datasets
- DomainTools — advanced DNS history and infrastructure pivoting
- RiskIQ / SpiderFoot — attack surface and infrastructure mapping

## 6.3 OSINT Best Practices

- **Archive immediately.** Screenshots with timestamps. Use `web.archive.org/save/[URL]` to permanently capture pages.
- **Cross-verify across 3+ independent sources** before including in a report.
- **Reused handles.** Same username on Telegram + GitHub + Twitter = strong link. Use Google: `"username" site:github.com OR site:twitter.com OR site:t.me`
- **Timing correlation.** Posting timestamps from social media that align with on-chain tx timestamps → timezone inference.
- **Language/style.** Repeated spelling patterns, emoji usage, phrasing across multiple accounts = stylometric fingerprint.
- **OPSEC when accessing dark web sources:** Use isolated VM, Tor, no personal accounts. Treat as legal gray area unless using aggregator services.
- **Think like the adversary.** Attackers take shortcuts: reuse usernames, recycle code, operate on predictable schedules. Look for laziness.
- **Set up proactive monitoring, not just reactive lookup.** Don't wait until an incident to check your tools — standing infrastructure saves you when the clock is running:
  - Set Etherscan wallet alerts on all addresses you're monitoring (free, email notifications)
  - Set up urlscan.io domain monitoring subscriptions for known scam infrastructure and campaigns you're tracking
  - Subscribe to ScamSniffer, MistTrack, and Chainabuse digest feeds
  - Add known attacker addresses to Arkham Intelligence watchlists (free tier) for real-time balance change alerts
  - Add Site Sentry (Telegram bot) to watch known phishing domains for front-end changes
  - Treat early awareness as a capability: catching a fund movement while the attacker is still bridging is qualitatively different from finding it three days later

**Protocol-level safeguards (post-hack advisory):**
Time-locks and withdrawal delays can block attacker extraction entirely. In the Bybit hack, **Mantle's 8-hour withdrawal delay blocked the attacker from extracting 15,000 cmETH** — a real-world example of this safeguard functioning correctly. When advising protocols post-incident, specifically review time-lock coverage on high-value withdrawal paths.

## 6.4 OSINT Limitations

- **Data overload.** The volume of social media, domain records, leak datasets, and threat feeds generates enormous noise. Many signals are irrelevant, outdated, or misleading. Structured workflows and experience are required to filter signal from noise.
- **False positives are common.** Community blacklists contain errors. Always validate with on-chain data.
- **Deception.** Sophisticated actors plant false OSINT trails. Cross-verify before concluding.
- **Ephemeral data.** Telegram groups disappear. Archive before they do.
- **OSINT cannot prove wallet ownership.** It builds circumstantial connections. Proof requires on-chain corroboration.
