# Advanced Techniques

These techniques are for complex investigations where basic tracing has stalled or the attacker has used obfuscation tools.

## 7.1 Time-Based Transaction Correlation

**When to use:** Funds passed through an instant swap service (eXch, ChangeNOW, RhinoFi) or private bridge that provides no transparent explorer.

**Method:**
1. Record: exact timestamp + exact amount deposited into opaque service on source chain
2. Find the service's hot wallet on the destination chain (Google: `"ChangeNOW" deposit address ethereum`)
3. Search outflows from that hot wallet within the same time window (±5 minutes)
4. Match by value (minus fee of ~0.1–1%)
5. The matching outflow = attacker's destination wallet

**Why it works:** Even when the service hides the link, physics is not obfuscated. Time and value are forensic anchors.

**Loopscale example (April 2025):**
- 10 SOL sent to ChangeNOW at 16:56:16 UTC
- 0.816 ETH received by attacker's ETH wallet at 16:56:59 UTC (43 seconds later)
- Match confirmed: same actor, cross-chain, through an opaque service

> Instruction: "Check the service's own hot wallet address on Etherscan. Filter its outbound transactions within the same 5-minute window as the deposit. Sort by amount matching the expected conversion rate."

## 7.2 Demixing Privacy Protocols

**Tools involved:** Tornado Cash (fixed denomination pools), Railgun (arbitrary amounts, zk-SNARKs), Wasabi/CoinJoin (Bitcoin)

**Important framing:** Demixing produces probabilities, not certainties. The goal is to narrow the candidate set and link exits to identifiable clusters downstream.

**Tornado Cash demixing methods:**
- **Timing analysis:** Deposits and withdrawals in similar time windows narrow the candidate set
- **Gas ratio analysis:** Same gas limit + gas price settings used for both deposit and withdrawal = behavioral fingerprint
- **Withdrawal clustering:** Addresses withdrawing in the same denominations on the same schedule = same operator
- **Linked gas wallets:** Who paid the withdrawal relay fee? Trace that funding wallet.
- **Post-exit tracking:** The moment funds leave Tornado, they're visible again. Monitor all withdrawal addresses and follow them downstream.
- **Statistical heuristics:** Stack timing + denomination + gas patterns → confidence score

**Railgun demixing:**
- **Value fingerprinting:** Arbitrary amounts can be fingerprinted (e.g., 123.456 ETH in = 123.456 ETH out minus fees)
- Track unshielding events and correlate with Tornado deposits or CEX entries

**CoinJoin (Bitcoin):**
- Multiple inputs combined in one tx → hard to separate. But:
  - Unmixed change outputs often link back to the original sender
  - Use **Wallet Explorer** or **OXT.me** to visualize CoinJoin clusters
  - Cross-reference timing and amounts against pre-mix inputs

**WazirX multi-layer demixing example:**
1. All stolen funds → Tornado Cash (deposit anchor = last confirmed position)
2. Tornado withdrawals → ETH→BTC swap on exchanges
3. BTC → CoinJoin transactions (thousands of micro-movements)
4. CoinJoin outputs → OTC brokers in Southeast Asia
5. Investigative approach: time-correlation at each layer, denomination matching, behavioral patterning, destination monitoring

## 7.3 Bridge Hopping Analysis

**What it is:** Tracking funds as they jump across multiple chains through bridge contracts.

**Step-by-step:**
1. Identify the bridge used (check attacker wallet for interactions with known bridge contracts)
2. Find the bridge's destination contract on the target chain (Google: `"[bridge name] contract address [destination chain]"`)
3. Use time-value correlation to match deposit → withdrawal
4. On Solana: look for Program-Derived Addresses (PDAs) — deterministic addresses that map back to Ethereum origins
5. Repeat for each subsequent hop

**Behavioral patterns to detect:**
- Rapid multi-chain hops within minutes = script-driven automation, not manual
- Consistent bridge sequence (e.g., ETH → BSC → Tron) = group fingerprint
- Liquidity-driven choices: USDT launderers prefer bridges with deep stablecoin pools
- Test transactions: attacker sends small amount first, then scales up

**Bybit hack example:** Funds moved through THORChain and eXch. Over 30,000 transactions tracked using a custom Dune dashboard by Tayvano. Same BTC laundering address linked to AlphaPo/Coinspaid 2023 hack.

> Free tool instruction: "Check `thorchain.net/txs` and filter by the attacker's address. For eXch, use time-value correlation from the depositing Ethereum address to find the receiving address on the output chain."

## 7.4 Large-Scale Data Analysis

**When to use:** Hundreds of wallets, thousands of transactions. Manual tracing is impossible.

**Dune Analytics (free):**
- Write SQL queries against decoded blockchain data
- Example query to find all outflows from a set of attacker wallets:
  ```sql
  SELECT
    "from" as attacker_wallet,
    "to" as destination,
    value / 1e18 as eth_amount,
    block_time
  FROM ethereum.transactions
  WHERE "from" IN (0xattacker1, 0xattacker2, ...)
    AND block_time > TIMESTAMP '2025-02-21'
  ORDER BY block_time
  ```
- Build dashboards to track flows visually in real time
- Reference: Tayvano's Bybit/Thorchain dashboard tracked 30,000+ transactions

> Instruction: "Go to dune.com → New Query → select 'ethereum.transactions' dataset → write a WHERE clause filtering by your attacker addresses → run. Fork any existing public Dune dashboard related to the incident and adapt it."

**Flipside Crypto (free):**
- Similar SQL analytics platform with cross-chain coverage including Solana, Avalanche, Osmosis

**Google BigQuery (free tier with limits):**
- Full Ethereum, Bitcoin, and other chain data available as public datasets
- Suitable for very large investigations requiring joins across multiple tables

## 7.5 Graph Analysis & Clustering

**What it is:** Modeling wallets as nodes and transactions as edges to reveal hidden network structures.

**Heuristic clustering methods:**
- **Common-input-ownership:** Multiple addresses used as inputs to the same transaction = same entity (Bitcoin)
- **Gas-fee wallet clustering:** Addresses funded by the same feeder wallet = same operator
- **Consolidation clustering:** Addresses that always send to the same final destination = same controller
- **Exploit-contract clustering:** All wallets that approved or interacted with same malicious contract = linked campaign

**Free graph tools:**
- **Breadcrumbs** (`breadcrumbs.app`) — visual graph of wallet relationships, free tier available
- **MetaSleuth** (`metasleuth.io`) — auto-generated fund flow map, cross-chain
- **Arkham Intelligence** (`arkhamintelligence.com`) — entity-level graph with free account
- **GraphSense** (open source, self-hosted) — full UTXO + account model graph analytics

**What to look for in graphs:**
- **Star networks:** One central wallet receiving from hundreds of victims (drainer collector)
- **Chain splitters:** One wallet fans out to dozens — peel chain beginning
- **Service reliance:** Multiple hacks converging on the same bridge/mixer/CEX
- **Overlap between incidents:** Two apparently unrelated hacks share a common laundering hub → same group

**Paid options:** Arkham Pro, Crystal Intelligence, Chainalysis Reactor — offer automated entity resolution and compliance-grade clustering. Worth it for professional investigations.

## 7.6 Pattern Recognition Across Cases

**Why it matters:** Laundering is recycled. Groups reuse playbooks that worked before. Recognizing patterns from past cases shortens future attribution timelines dramatically.

**Lazarus Group (DPRK) Signature Pattern:**
```
Exploit → Tornado Cash (100 ETH batches, multiple rounds)
→ Optional: Railgun layer
→ Bridge to BNB Chain or Tron
→ Convert to USDT or BUSD
→ OTC brokers (Southeast Asia or Middle East)
→ Cash-out
```

When you see: multiple rounds of Tornado Cash in 100 ETH denominations, followed by a Tron USDT bridge → high-confidence Lazarus indicator. Cross-check with OFAC and UN sanctions lists.

**Inferno/Angel Drainer Pattern (approval scams):**
```
Phishing site → setApprovalForAll() or unlimited approve()
→ Same drainer contract (hundreds of victims)
→ Collector wallet consolidates all stolen assets
→ Bridge to Tron → OTC cash-out
```

**Bridge Hopper Pattern (rapid multi-chain):**
```
Hack → Immediate token swap (DEX, no CEX risk)
→ Bridge hop 1 → Bridge hop 2 → Bridge hop 3 (within 30 minutes)
→ Stablecoin conversion → OTC or exchange with weak KYC
```

**Build your own pattern library:**
> Keep a running document of laundering sequences you observe. Over time, this becomes a personal threat intelligence database. When a new incident occurs, compare its pattern to your library before starting from scratch.
