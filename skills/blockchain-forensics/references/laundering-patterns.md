# Laundering Pattern Library

Reference table of known laundering techniques and how to detect and follow them:

| Technique | Detection Method | Key Tool (Free) |
|---|---|---|
| Peel chain | Trace linear chain of equal-amount hops | Breadcrumbs, MetaSleuth |
| Tornado Cash mixing | Post-exit monitoring, timing, gas ratio | Etherscan, Dune |
| Railgun shielding | Value fingerprinting on unshield events | Etherscan, Arkham |
| CoinJoin (Bitcoin) | Change output analysis | OXT.me, Wallet Explorer |
| Cryptomixer (Bitcoin) | Custodial BTC mixer (operating since 2016); pools deposits, redistributes to new addresses after time delay. Look for: BTC inflows from known hack wallets followed by equivalent outflows to new cold addresses with time gaps | Mempool.space, OXT.me |
| Bridge hopping | Time-value correlation, bridge contract monitoring | Bridge explorers, Dune |
| Instant swap obfuscation | Time-value correlation (±5 min window) | Etherscan, chain explorer |
| CEX micro-deposits | Pattern-match small amounts to hot wallets | Etherscan, Arkham |
| OTC cash-out (Tron USDT) | Identify Tron address clusters receiving large USDT | Tronscan, MistTrack |
| P2P off-ramp (Binance P2P, LocalBitcoins, HodlHodl) | Attacker sells crypto directly for fiat via burner/purchased-KYC identities; minimal on-chain trace after P2P exchange — pivot on the deposit address to the P2P platform, report to exchange compliance | Exchange cooperation required |
| Stablecoin bridging | Follow USDT/USDC via bridge contracts to Tron/BNB | Tronscan, BSCScan |
| Fake/stolen identity CEX | Flag for exchange cooperation; not traceable on-chain alone | Report to exchange |
| Unregulated exchange off-ramp (Huione, Xinbi, Grantex) | **Huione**: Cambodia-linked platform with Telegram/WeChat presence; used by pig butchering rings and fraud networks to off-ramp via informal agents. **Xinbi**: weak-KYC exchange; accepts near-anonymous trading. **Grantex**: Russia-based; darknet and ransomware cashout. Detection: trace Tron USDT flows to receiving addresses associated with these platforms; report to partner exchanges and OFAC | MistTrack, Arkham, exchange cooperation |
| Dusting / micro-probe transactions | Identify small test amounts sent before major movement; link probe wallet to main actor | Etherscan, Breadcrumbs |
| CEX deposit address reuse | Same deposit address used across multiple separate hacks → single operator | Etherscan, Arkham |
| Privacy pool chaining | Reconstruct each layer separately; monitor all exits | Dune (custom query) |
