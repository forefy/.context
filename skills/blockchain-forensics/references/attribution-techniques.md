# Attribution Techniques

Use these techniques when basic tracing has established fund flows and the goal shifts to identifying who controls the wallets.

## 5.1 Transaction-Based Attribution

**Common Input/Output Patterns:**
- Multiple addresses sending to the same CEX deposit wallet → same entity
- Same withdrawal batch distributing to multiple wallets → same source
- Stolen funds consolidated into a previously used wallet → links to prior hack
- Assets split then recombined at one endpoint → reveals ultimate controller
- Collector addresses aggregating hundreds of victim flows (drainer campaigns)

*Example: Inferno Drainer contract `0x000037bB05B2CeF17c6469f4BcDb198826Ce0000` — thousands of victims all funneled into one contract, which redistributed to attacker-controlled collectors.*

**Gas-Fee / Funding Wallet Attribution:**
- Multiple wallets topped up with identical gas amounts in a short timeframe → same operator
- Gas feeder that used funds from a previous hack → links two incidents
- Gas supplied via Tornado Cash withdrawals → look at the withdrawal timing/denomination pattern
- Private bridge funding: correlate by timestamp ± value across chains

*Example: WazirX hack — test wallet `0x6eedf9...` received six 0.1 ETH top-ups from Tornado Cash eight days before the main incident, funding SHIB test transactions.*

**Peel Chains:**
- Funds split into fixed amounts, forwarded through a linear chain of wallets
- Each hop slightly reduces the amount (gas fees), creating a traceable "peel" effect
- Map the entire peel chain as a graph; the terminal wallet is the consolidation point

**Transaction Graph Analysis:**
- Wallets repeatedly interacting with same collector or broker
- Star-shaped patterns: one funder → many children
- Dense clusters around exploit contracts or drainer services
- Convergence of multiple laundering paths into one endpoint

## 5.2 Infrastructure / Interaction Attribution

**Drainer and Exploit Contracts:**
- Thousands of victims approving the same contract → natural attribution anchor
- Even when collector wallets rotate, the drainer contract ties all activity together

**Exploit Code Reuse:**
- Same bytecode in different incidents = same group or shared toolkit
- Check contract bytecode on Etherscan → "Similar Contracts" feature shows matches
- Deployment wallet often the same across multiple malicious contract launches

**Deployment Wallets:**
- Trace who deployed the malicious contract → that wallet often deployed others
- One developer wallet can attribute dozens of contracts to the same actor

## 5.3 Cross-Chain Attribution

**Bridging and Stablecoin Laundering Patterns:**
- Stolen ETH → USDT/USDC → bridged to Tron (high liquidity for OTC)
- Track which addresses consistently receive bridged stablecoins after hacks

**Repeated Bridge Preference:**
- Groups reuse the same bridges across incidents (THORChain, Allbridge, Multichain, Wormhole)
- Consistent bridge choice = attribution fingerprint
- Monitor bridge inflows/outflows to match source chain wallets with destination recipients

**Timing Correlation in Semi-Private Bridges (eXch, ChangeNOW, RhinoFi):**
- Record: exact timestamp + amount deposited on source chain
- Find: outflow of equivalent value (minus fee) from bridge hot wallet within tight time window
- Match: deposit and withdrawal = same actor

**Convergence at OTC Brokers:**
- Multiple hacks converging at same Tron USDT broker address = shared group
- Lazy Group / Lazarus Group: repeatedly used same Southeast Asian OTC brokers

*Example: Bybit hack — ETH consolidated at `0xd6a164...` → moved to BTC → BTC address `bc1qt2w...` linked to AlphaPo/Coinspaid hack of 2023 → same laundering infrastructure, same group.*

> ⚠️ **False Positive Warning:** Cross-chain attribution is the technique most prone to misattribution. Even small errors in timing or value matching can redirect an entire investigation toward the wrong actor. Before attributing any wallet via bridge analysis, verify the match holds on at least two independent signals (timing + value + behavioral pattern). When in doubt, classify as "possible link — needs further corroboration," never as confirmed attribution.

## 5.4 Behavioral Attribution

**Timing Habits:**
- Transactions consistently executed at the same hours of day → timezone inference
- Lazy Group / Lazarus: often active during Asian business hours / North Korean working day
- Automation: transfers executing every N minutes → script-driven, not manual
- **Compliance gap exploitation:** Sophisticated attackers deliberately time large moves for weekends, public holidays, or late-night hours when exchange compliance teams are slow or offline. Multiple hours of lag before a freeze request is actioned = attacker advantage. Investigators should flag this pattern when it appears — it indicates deliberate operational awareness, not coincidence.

**Stablecoin and Asset Preferences:**
- Consistent conversion to USDT on Tron → OTC/cash-out preference
- Some groups prefer DAI or USDC depending on their exit markets
- Cross-cluster matching: track which stablecoin flavors appear consistently across hacks

**Protocol and Route Choices:**
- Always swapping via Uniswap v3, then bridging via THORChain = fingerprint
- Curve pools preferred for large stablecoin swaps (deep liquidity)

**Fixed Denominations:**
- Tornado Cash: fixed pool sizes (0.1, 1, 10, 100 ETH) — consistent denomination choice = pattern
- Peel chains often move near-identical amounts step by step

**Cash-Out Consistency:**
- Different hacks converging at the same OTC broker on Tron = linked operations
- Lazarus Group: Tornado (100 ETH batches) → Bridge → Tron USDT → Same OTC broker
