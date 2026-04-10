# Tool Reference (Free-First)

## 9.1 Block Explorers (Always Free)
- **Etherscan** (etherscan.io) — Ethereum: txs, internal txs, token approvals, contract reads
- **Solscan** (solscan.io) — Solana
- **BSCScan** (bscscan.com) — BNB Chain
- **Tronscan** (tronscan.org) — Tron (critical for USDT OTC tracking)
- **Snowtrace** (snowtrace.io) — Avalanche
- **Arbiscan** (arbiscan.io) — Arbitrum
- **Polygonscan** (polygonscan.com) — Polygon
- **Mempool.space** — Bitcoin
- **Wormholescan** (wormholescan.io) — Wormhole bridge
- **THORChain explorer** (thorchain.net) — THORChain swaps

## 9.2 Visual Tracing & Graph Tools (Free Tier Available)
- **Breadcrumbs** (breadcrumbs.app) — visual graph tracing, address labeling, export
- **MetaSleuth** (metasleuth.io) — auto fund flow maps, cross-chain
- **Arkham Intelligence** (arkhamintelligence.com) — entity attribution, real-time balances, alerts
- **DeBank** (debank.com) — portfolio view, approval history across EVM chains
- **Nansen** (nansen.ai) — whale movement monitoring, bridge outflow tracking, protocol-specific wallet surveillance; especially useful for detecting large-scale coordinated movements in real time

## 9.3 Smart Contract Decoding (Free)
- **Phalcon** (phalcon.xyz) — decoded DeFi transaction traces
- **Tenderly** (tenderly.co) — transaction simulation, full call stack, free tier

## 9.4 Analytics & Querying (Free)
- **Dune Analytics** (dune.com) — SQL queries on blockchain data, community dashboards
- **Flipside Crypto** (flipsidecrypto.xyz) — multi-chain SQL analytics
- **OXT.me** (oxt.me) — Bitcoin-specific transaction graph and CoinJoin cluster analysis
- **Wallet Explorer** (walletexplorer.com) — Bitcoin CoinJoin and clustering analysis

## 9.4a Curated Tools Reference Sheet
The author (@somaxbt) maintains a comprehensive tools sheet organized by use case (explorers, attribution, visualization, monitoring, compliance):
> `sheets.fileverse.io/0xD3edEFbfe7934c685Ef182A38a91cB70fABE45c7/2`
> Start with the free tools column — build foundational skills before moving to commercial platforms.

## 9.5 OSINT Tools (Free)
- **urlscan.io** — scan URLs, find embedded wallet addresses, infrastructure mapping
- **crt.sh** — SSL certificate search, find related domains
- **web.archive.org** — capture and retrieve archived web pages
- **SecurityTrails** (free tier) — DNS history, subdomain search
- **Have I Been Pwned** (haveibeenpwned.com) — email breach check
- **WHOIS** (who.is) — domain registration details
- **Chainabuse** (chainabuse.com) — crowdsourced scam address reports
- **ScamSniffer** (scamsniffer.io) — phishing and drainer database
- **sanctioned.us** — fast OFAC SDN search by address

## 9.6 Revoke / Approval Management & Victim-Facing Protection

**Approval revocation (for victim support):**
- **Revoke.cash** — view and revoke all token approvals by address
- **Etherscan Token Approval Checker** — built into Etherscan, free

**Browser extensions for transaction safety (recommend to victims and for investigator's own monitored wallets):**
- **Wallet Guard** (`walletguard.app`) — detects malicious contracts, flags suspicious approvals, and blocks known phishing domains before you sign. Supports EVM chains.
  > Instruction: `Install from the Chrome Web Store → it automatically intercepts wallet connection requests and displays a risk assessment. When a transaction requests token approval, it shows what the contract can access before you confirm.`
- **Pocket Universe** (`pocketuniverse.app`) — simulates transactions and shows you exactly what will change in your wallet before you sign. Catches approvals disguised as benign actions.
  > Instruction: `Install from Chrome Web Store → any time you sign a transaction in MetaMask or other injected wallets, Pocket Universe shows a preview of token movements. If it shows unexpected token outflows or unlimited approvals, reject the transaction.`
- **Scam Sniffer** (`scamsniffer.io`) — real-time phishing domain detection; warns when you navigate to a known drainer site

## 9.7 Paid Tools (Acknowledge, Don't Require)
These are powerful, worth recommending for institutional or large-scale investigations:
- **Chainalysis Reactor** — industry standard for law enforcement
- **TRM Forensics / TRM Phoenix** — advanced tracing, automated chain-hop analysis
- **Crystal Intelligence** — UTXO + EVM tracing with compliance reporting
- **Elliptic Investigator** — graph analysis, AML scoring
- **Arkham Pro** — advanced entity attribution, premium alerts
- **Dehashed** — breach data cross-search
- **DomainTools** — advanced DNS infrastructure pivoting

## 9.8 Community Intelligence Sources (Always Check First)
- **ZachXBT** (@zachxbt on X, Telegram: t.me/investigations) — highest-quality public attribution work
- **Tayvano** (@tayvano_ on X) — advanced wallet security and drainer tracking
- **PeckShield** (@PeckShieldAlert) — real-time exploit alerts
- **Cyvers** (@CyversAlerts) — DeFi anomaly detection
- **SlowMist / MistTrack** (@MistTrack_io) — AML and incident reporting
- **SEAL-ISAC** — dual role: (1) structured threat intelligence sharing network for vetted security professionals (apply for access at seal.org); (2) public reporting and aggregation platform for crypto-native security incidents, extortion threats, and scam address databases. Check it for address lookups alongside Chainabuse and ScamSniffer. Report extortion/blackmail campaigns here.

## 9.9 Terminology Reference
- **Elliptic Glossary** (`elliptic.co/learning-resources#glossary`) — authoritative reference for blockchain investigation terminology: mixing, clustering, heuristics, AML terms, privacy protocol mechanics. Use when encountering unfamiliar terms in reports or evidence.
