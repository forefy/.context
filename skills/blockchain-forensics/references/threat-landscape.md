# Threat Landscape Reference

Use this file to identify the type of crime being investigated and brief the user on known patterns so they know what to expect on-chain.

## 3.0 Scale Context (for Scoping and Threat Briefing)

Use these figures when helping users understand the severity of a threat type or justify investigation effort:

| Metric | Figure | Source |
|---|---|---|
| Total lost to crypto scams/hacks/state attacks (5 years) | $100B+ | Article 1 |
| Illicit crypto volume 2023 (peak) | $58.7B | TRM Labs |
| Illicit crypto volume 2024 | $44.7B | TRM Labs |
| Pig butchering losses Jan 2020–Feb 2024 | $75B | University of Texas |
| Pig butchering US losses 2024 alone | $5.8B | FBI IC3 |
| Approval phishing losses since May 2021 | $2.7B | Chainalysis |
| Wallet drainer losses in 2024 alone | $494M | ScamSniffer |
| Wallets compromised by drainers in one year | 332,000 | ScamSniffer |
| Stolen from Coinbase users via social engineering | $340M+ | ZachXBT/tanuki42 |
| Single social engineering theft (Coinbase) | $243M | ZachXBT |

## 3.1 Protocol-Level Exploits and Bridge Hacks
- Flash loan attacks, logic flaws, oracle manipulation, reentrancy
- Cross-chain bridge drain by bypassing validation
- Proxy upgrade manipulation (e.g., Bybit Safe UI spoofing)
- Immediate asset conversion post-exploit: freeze-prone stablecoins (USDT/USDC) → ETH/SOL/TRX
- Rapid fund splitting across 40–100+ wallets (peel chains)
- Dormancy periods: funds may sit idle for days–months before next move

## 3.2 Wallet Drainers & Approval Scams
- Drainer-as-a-Service (DaaS): Inferno Drainer, Monkey Drainer (pioneer/model setter), Angel Drainer, Medusa Drainer, Ace Drainer
- DaaS economics: operators sell ready-made toolkits (phishing templates, Telegram bots, dashboards, laundering scripts) to affiliates in exchange for a % of stolen funds
- Geographic base: Russia, Eastern Europe, Southeast Asia — leverage bulletproof hosting and encrypted Telegram channels for advertising and support
- ERC-20 `approve(spender, uint256.max)` grants unlimited access; no private key needed
- NFT `setApprovalForAll(spender, true)` drains entire collections
- `transferFrom()` executes silently, often hours or days after approval
- Victim is lured to clone site via compromised Discord, Telegram, Twitter/X DM, paid ad
- On-chain pattern: hundreds of victims → single collector contract → attacker wallet

**What to look for on-chain:**
- Check victim's token approval history on Etherscan (Token Approval Checker)
- Identify the malicious spender contract
- Map all other victims who approved the same spender
- Trace collector contract's outflows → attacker's consolidation wallet

## 3.3 Pig Butchering / Romance Scams
- Trust is built over days/weeks via dating apps, Telegram, wrong-number SMS
- Fake investment platform shows fabricated gains
- Victims are urged to deposit more; withdrawal blocked by fake fees/taxes
- Criminal infrastructure: Southeast Asian crime syndicates (Myanmar, Cambodia, Laos)
- On-chain: funds flow to centralized collector wallets; eventually off-ramped via CEX or OTC

**What to look for on-chain:**
- Victim sends to a wallet they believe is "their portfolio" — that wallet sends to a laundering hub
- Look for convergence: many different victims → same destination cluster
- Check Chainabuse, ScamSniffer for reported destination addresses

## 3.4 Phishing Attacks

Phishing targets **users of specific platforms or products** — waiting for them to visit a fake interface, connect their wallet, or enter sensitive information. No human interaction required — just a convincing trap. Transactions are irreversible; wallets are drained before victims realize.

**Statistics:** $2.7B in losses since mid-2021 (Chainalysis); 330,000+ wallets compromised in 2023 alone causing $295M in losses (ScamSniffer). Phishing kits (drainer templates, Telegram dashboards, laundering scripts) are sold as plug-and-play packages on underground markets.

**How it works:**
1. Attacker clones a trusted Web3 site (NFT mint, DeFi staking portal, wallet download page) — often pixel-perfect
2. Distributes via: Discord/Telegram compromised channels, Twitter/X hijacked accounts, Google/social media sponsored ads that outrank the real site, email campaigns
3. User prompted to: sign an `approve()` or `setApprovalForAll()` transaction, enter seed phrase in a form, or download a fake wallet extension containing malware
4. Funds drained silently via the approval, or immediately via the seed phrase

**Red flags:**
- URL slightly off from official domain (e.g., `uniswap-launchpad.org` vs `app.uniswap.org`)
- Transaction request uses vague labels like "verify", "claim", "continue" — not specific action names
- Any website or form asking for your seed phrase or private key — no legitimate platform ever does this
- Site prompts you to download a browser extension or wallet file without verified instructions
- Unexpected pop-up or redirect when visiting a project from a community link

**Prevention:**
- Bookmark official project URLs — never navigate from DMs, Discord announcements, or search results
- Use **Wallet Guard** or **Pocket Universe** browser extensions — these simulate transactions and flag suspicious approvals before you sign
- Use **Scam Sniffer** to detect known phishing domains in real time
- Never enter seed phrases on any website
- Use a hardware wallet — requires physical button confirmation, blocking silent approvals even if you land on a phishing site

**On-chain investigation pivots:**
- Pull victim's token approval history on Etherscan → identify the malicious spender contract
- Map all other victims who approved the same spender → full drainer victim set
- Trace collector contract outflows → attacker's consolidation wallet
- Search the phishing domain on urlscan.io → find embedded wallet addresses, related domains, infrastructure

## 3.4b Address Poisoning

Attacker sends a **zero-value or dust transaction** from a wallet address crafted to visually match the first/last characters of a trusted contact's address. The poisoned address then appears in the victim's wallet history — when they later copy from history to send funds, they paste the attacker's address instead.

**Statistics:** 270+ million attempts targeting ~17 million users on Ethereum and BNB Chain in 2024; 6,633 successful incidents totaling $83.8M in losses; single case: $68M in wBTC lost in May 2024 (victim sent to a poisoned address 1 character different from intended recipient).

**How it works:**
1. Attacker generates a vanity address matching the first ~6 and last ~4 characters of a victim's frequent recipient (e.g., `0x5fB2...D4c8` → `0x5fB2...D4c3`)
2. Sends a 0-value USDT or 0 ETH transaction from the lookalike address to the victim — no malicious payload, just a history plant
3. When the victim next sends funds to the real address, they scroll their history, see the fake one first, and paste it without checking the full string
4. Funds are irreversible — the transfer was to a valid address

**Red flags:**
- Zero-value or tiny dust transactions from an address you didn't initiate contact with
- Address in your history that matches the first and last characters of a known contact but differs in the middle — always verify the full string, not just start/end
- Any out-of-context transaction you didn't initiate (no airdrop claim, no DEX interaction from you)

**Prevention:**
- Never copy wallet addresses from your transaction history — use a saved address book or contact list instead
- Always verify the **full address**, not just start and end characters, when pasting
- Use wallets with address books / whitelisting (Rabby Wallet, Wallet Guard, Fireblocks for teams)
- Flag and hide zero-value transactions — do not interact with them
- For large amounts: verify the recipient address out-of-band (confirm by voice, separate channel) before sending

**On-chain investigation:**
- Look for $0 dust transactions from near-identical addresses in the victim's history
- Vanity address generators leave traces — check if the attacker's address has sent the same dust pattern to thousands of other wallets (it usually has — map the full poisoning campaign)

## 3.5 Scam Tokens, Fake Airdrops, Rug Pulls & Honeypots

Four related attack types that exploit **token trust assumptions, DEX mechanics, and UI design** to extract value without ever needing to compromise the victim's wallet:

- **Scam Tokens** — ERC-20 tokens with names mimicking real assets (e.g., `ETH2.0`, `UNI-Reward`, `USDTDrop`), distributed via airdrop/dusting. Either worthless bait or contain malicious approval logic triggered via DEX interaction
- **Fake Airdrops** — scam tokens with phishing URLs embedded in the token name or transfer memo (e.g., `"Claim your $500 Airdrop at airdrop-claim[.]xyz"`). Goal: redirect victim to phishing site where they sign malicious approval or enter seed phrase
- **Rug Pulls** — seemingly legitimate token/project suddenly removes all liquidity or disables key functions after attracting investors. Preceded by influencer shills, bot-generated volume, Telegram hype. Especially common with memecoins and fast-moving DEX launches
- **Honeypots** — smart contracts that allow buying but block or tax selling (50–100% sell tax). Look normal on DEX interfaces; require reading the contract to detect

**Red flags — Scam Tokens/Airdrops:**
- Token appeared in your wallet unprompted — especially if its name contains "reward", "bonus", "airdrop", or mimics a real project
- Token name or transfer memo contains a URL — this is the phishing hook
- Token has no liquidity or swap fails immediately
- Contract address is unverified (no source code on Etherscan/BscScan)

**Red flags — Rug Pulls:**
- No locked liquidity — use TokenSniffer, Mudra, or DexTools to verify LP lock
- Anonymous devs with no traceable prior projects
- Sudden rapid price action with no fundamentals
- Contract owner retains control over critical functions (pause trading, change tax rate, mint new tokens)
- Ownership not renounced

**Red flags — Honeypots:**
- Token can be bought but not sold — test with a tiny amount first
- High or hidden sell taxes (70–100%) — check tokenomics before committing
- Perfect green chart with zero red candles and constant buying = likely fake volume or honeypot trap
- Contract source code unverified on chain explorer

**Prevention:**
- Never interact with unknown tokens in your wallet — do not try to swap, approve, or transfer them
- Use token safety tools **before** buying: TokenSniffer (`tokensniffer.com`), Honeypot.is (`honeypot.is`), RugDoc, CheckMate
  > Instruction: `Go to honeypot.is → enter the contract address → it simulates a buy and sell → if sell fails or shows >10% tax, it's a trap.`
- Hide suspicious airdrops in your wallet to avoid accidental interaction
- Use reputable aggregators (1inch, CowSwap, Matcha) — they apply filters blocking tokens with known malicious logic
- Always test with a small amount before committing real funds

**On-chain investigation pivots:**
- Trace sudden LP removal: find the LP contract's `removeLiquidity` or `burn` events
- Trace dev wallet: find the contract deployer → track all their wallet activity and other contract deployments
- Map the coordinated buy-side: many distinct wallets buying in a short window → look for common funding source (CEX withdrawal from one account, funded by same source wallet)
- Fake volume pattern: identify wallets buying and selling the same token within minutes of each other → same entity cycling funds to show activity

## 3.6 Social Engineering / Impersonation
- Fake support agents, VC firms, job offers (often DPRK-linked IT workers)
- DPRK IT workers operate multiple fake identities across platforms; reuse code styles and GitHub handles across campaigns — these repos are traceable via OSINT
- Malicious file downloads (PDF, "NDA", job assessment) deploy malware to extract private keys
- Victim signs transaction under false pretense (e.g., Bybit: spoofed Safe UI)
- $340M+ stolen from Coinbase users alone via social engineering (2024)

## 3.6b Crypto Blackmail & Extortion

Unlike phishing or wallet drainers, these attacks rely on **emotional manipulation, psychological pressure, and social leverage** — not technical deception. Two modes: bulk automated campaigns (sent to thousands, low effort) and targeted campaigns (aimed at public figures, NFT collectors, visible on-chain whales).

**Crypto extortion is escalating globally and increasingly involves physical violence:** French authorities have documented kidnappings of crypto executives and their family members, with ransom demands up to €10M (Ledger co-founder David Balland, kidnapped Jan 2025; Paymium CEO's family, targeted May 2025). New York: crypto investor tortured to gain wallet access (May 2025). London: U.S. tourist drugged and robbed of $123K in crypto via fake Uber (May 2025). Digital extortion enables physical targeting — **radical blockchain transparency becomes a weapon when personal privacy is neglected**.

**How it works:**
1. Attacker collects real or fabricated personal data: data breaches, blockchain analytics (Etherscan/Arkham to link wallet to identity), leaked email/password pairs, doxxed ENS names, social media profiles, GitHub commit history
2. Victim receives threatening email, DM, or message with enough personal detail to appear credible (may include a leaked password, a real wallet address, or partial transaction history)
3. Demand is issued: Bitcoin, Monero, or USDT wallet address + deadline. Mass campaigns: $300–$3,000. Targeted: up to millions
4. Some attackers use "proof of life" partial leaks to enforce urgency, or escalate threats with each follow-up

**Red flags:**
- Claim includes a real (but stale) password — sourced from a historical breach, not live access
- Claim of webcam access, browser surveillance, or malware installation with no supporting evidence
- Wallet address provided for payment with a very short deadline
- Message includes your wallet address linked to identity it shouldn't have access to (but actually sourced from OSINT)

**Response protocol (for investigators advising victims):**
1. **Do not pay** — payment confirms vulnerability and often triggers more demands
2. Document everything: screenshot the message, note the wallet address provided
3. Check the provided attacker wallet on Chainabuse and blockchain explorers — it's often already reported by other victims
4. Look up the included password on `haveibeenpwned.com` — usually from a breach years old, not live compromise
5. Report to: local cybercrime unit, FBI IC3 (ic3.gov), **SEAL-ISAC**, Chainabuse

**On-chain investigation if victim has paid:**
- Trace the extortion wallet: look for multiple incoming payments from different victims (convergence pattern)
- Often routes to Bitcoin (Monero untraceable) or USDT on Tron → OTC
- If Bitcoin: use `oxt.me` or `Wallet Explorer` to analyze clustering and CoinJoin usage

## 3.7 Nation-State Actors
- **Lazarus Group (DPRK):** Most prolific — responsible for Ronin, Harmony, Atomic Wallet, WazirX, Bybit, and dozens of others. Signature pattern: Tornado Cash (100 ETH batches) → Bridge → Tron USDT → OTC.
- **Gonjeshke Darande (Predatory Sparrow):** Iranian-linked group that exploited Iranian exchange **Nobitex** as part of a regionally targeted financial disruption. Represents nation-state use of crypto attacks for geopolitical disruption, not just theft.
- Nation-state actors exploit cross-border jurisdictional gaps — enforcement stalls even when on-chain evidence is indisputable, because no unified global legal standard exists.

## 3.8 Challenges in Blockchain Forensics

These are structural constraints that every investigator must understand before starting a case:

- **Cross-border jurisdiction:** Attackers routinely exploit regulatory gaps between countries. Even with clear on-chain evidence, legal action requires a jurisdiction willing and able to act.
- **No unified global standard:** Enforcement capability varies drastically by country. Funds that reach exchanges in low-regulation zones are often unrecoverable through legal channels.
- **Speed asymmetry:** Attackers can bridge, mix, and off-ramp funds in minutes. International legal processes take weeks to months.
- **Pseudonymity wall:** On-chain data proves *what* happened with certainty, but proving *who* did it requires OSINT, exchange cooperation, or law enforcement subpoenas.
- **Investigation cost vs. recovery:** Not every case justifies full pursuit. The investigation must be proportionate to realistic recovery potential.
- **Tooling gaps on niche chains:** Mature chains (Ethereum, Solana) have rich explorer and analytics ecosystems. Newer or obscure chains may require raw log parsing with no visualization support.

## 3.9 Physical Theft & Wrench Attacks

Physical theft **bypasses all digital security** — coercion, violence, or device theft can defeat even the strongest wallet setup. Investigators are increasingly asked to trace on-chain movement post-physical-compromise.

**Wrench attacks** (colloquial: `$5 wrench attack`) — direct coercion to force a victim to transfer funds, reveal seed phrases, or unlock hardware wallets under physical threat. Increasingly organized and targeting individuals with visible on-chain wealth.

**Recent high-profile incidents (2024–2025):**
- **Paris, May 2025:** Crypto CEO's father kidnapped and mutilated; separate attempted abduction of his daughter and grandson
- **France, Jan 2025:** Ledger co-founder David Balland and partner kidnapped; mutilated; €10M ransom demanded
- **New York, May 2025:** Crypto investor allegedly tortured over multiple weeks to force wallet access
- **London, May 2025:** U.S. tourist drugged and robbed of $123K in crypto via a staged fake Uber
- **U.S., 2024:** Crime ring conducted coordinated home invasions across four states; $260M+ stolen

**Attack methods:**
- **On-chain profiling as targeting step:** Attackers use Etherscan, Arkham, and social media to identify high-value holders. ENS names, public NFT collections, conference talks, on-chain transaction sizes all serve as target identifiers
- **Home invasion / office raid:** Armed entry, victim forced to reveal seed phrase or unlock devices. May involve advance surveillance or insider information about cold wallet storage locations
- **Device theft:** Laptops, phones, hardware wallets stolen during travel. Attacker attempts access before victim can trigger remote wipe
- **Kidnapping for ransom:** Multiple global cases particularly in Europe and Latin America — victim forced to initiate large transfers
- **Social engineering as setup:** Fake business meetings, Airbnb meetups used to gain physical proximity before the attack

**On-chain investigator's role after physical theft:**
- Identify the receiving wallet addresses the victim was forced to transfer to
- Begin standard fund tracing (Phases 3–5) — even forced transfers leave the same on-chain trail
- Check if receiving address is new (created for this incident) or part of a known criminal cluster
- Physical theft cases often route to Bitcoin or Monero for cash-out — apply Bitcoin UTXO clustering techniques
- Coordinate with law enforcement; physical violence cases usually have a parallel criminal investigation

**Prevention guidance (for advising clients):**
- Never publicly display wallet holdings or large trades on social media — even ENS names and NFT profiles create targeting surface
- Use multisig or time-locked withdrawal setups — makes instant forced transfers much harder under duress
- Keep primary holdings in hardware wallets stored in undisclosed, separate locations — not on portable devices or in predictable home locations
- Split holdings across multiple wallets with limited balances — contain damage if one is compromised under pressure
- Use a "duress wallet" — a low-balance wallet you can hand over without exposing primary holdings
- Avoid predictable routines when accessing high-value wallets; vary locations, times, devices
- Train household members never to reveal passwords or seed phrases even under threat
- Traveling with crypto gear: use dummy laptops, burner devices, avoid opening wallet apps in public
