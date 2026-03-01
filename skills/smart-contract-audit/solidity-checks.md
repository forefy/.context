# Solidity-Specific Audit Checks

## Protocol Context Lookup

After detecting the protocol type, load the corresponding protocol context file from `reference/solidity/protocols/`. Each file contains protocol-specific preconditions, detection heuristics, and historical exploit patterns cross-referenced to fv-sol-X IDs.

| Detected Protocol Characteristics | Load File |
|------------------------------------|-----------|
| AMM, DEX, swap, Uniswap-style, Curve-style, order book, concentrated liquidity | [reference/solidity/protocols/dexes.md](reference/solidity/protocols/dexes.md) |
| Lending, borrowing, collateral-backed money market, flash loan, Aave-style, Compound-style | [reference/solidity/protocols/lending.md](reference/solidity/protocols/lending.md) |
| Bridge, cross-chain, message passing, lock-and-mint, LayerZero, Wormhole | [reference/solidity/protocols/bridges.md](reference/solidity/protocols/bridges.md) |
| Algorithmic stablecoin, rebase token, seigniorage, endogenous collateral, Luna/UST-style | [reference/solidity/protocols/algo-stables.md](reference/solidity/protocols/algo-stables.md) |
| Decentralized stablecoin, exogenous collateral, CDP-backed stable, DAI-style | [reference/solidity/protocols/decentralized-stablecoin.md](reference/solidity/protocols/decentralized-stablecoin.md) |
| Reserve currency, treasury-backed token, Olympus-style, protocol-owned liquidity | [reference/solidity/protocols/reserve-currency.md](reference/solidity/protocols/reserve-currency.md) |
| Yield farming, yield aggregator, strategy vault, auto-compounder, ERC-4626, Yearn-style | [reference/solidity/protocols/yield.md](reference/solidity/protocols/yield.md) |
| Staking pool, liquid staking, validator pool, ETH staking, restaking | [reference/solidity/protocols/staking.md](reference/solidity/protocols/staking.md) |
| Derivatives, perpetuals, funding rate, leveraged positions, on-chain perps, GMX-style | [reference/solidity/protocols/derivatives.md](reference/solidity/protocols/derivatives.md) |
| Synthetics, synthetic asset issuance, debt pool, mirror asset, Synthetix-style | [reference/solidity/protocols/synthetics.md](reference/solidity/protocols/synthetics.md) |
| NFT marketplace, order book marketplace, Seaport-style, on-chain NFT auction, NFT lending market | [reference/solidity/protocols/nft-marketplace.md](reference/solidity/protocols/nft-marketplace.md) |
| NFT minting, gaming, play-to-earn, gamefi, NFT staking | [reference/solidity/protocols/nft-gaming.md](reference/solidity/protocols/nft-gaming.md) |
| Liquidity manager, position manager, Arrakis-style, Gamma-style, concentrated liquidity wrapper, Uniswap v3 position vault | [reference/solidity/protocols/liquidity-manager.md](reference/solidity/protocols/liquidity-manager.md) |
| Governance, DAO, on-chain voting, timelock, treasury management | [reference/solidity/protocols/governance.md](reference/solidity/protocols/governance.md) |
| Token launchpad, IDO, token sale, vesting, fair launch | [reference/solidity/protocols/launchpad.md](reference/solidity/protocols/launchpad.md) |
| On-chain insurance, coverage protocol, risk pool, parametric insurance, claims | [reference/solidity/protocols/insurance.md](reference/solidity/protocols/insurance.md) |
| Index protocol, basket token, index rebalancing, tokenized portfolio, Set Protocol-style | [reference/solidity/protocols/indexes.md](reference/solidity/protocols/indexes.md) |
| Protocol utility service, fee router, keeper network, meta-aggregator, merkle airdrop | [reference/solidity/protocols/services.md](reference/solidity/protocols/services.md) |
| Privacy protocol, on-chain mixing, zero-knowledge proof, shielded pool, Tornado Cash-style | [reference/solidity/protocols/privacy.md](reference/solidity/protocols/privacy.md) |
| Real world asset tokenization, tokenized securities, permissioned token, RWA on-chain representation | [reference/solidity/protocols/rwa-tokenization.md](reference/solidity/protocols/rwa-tokenization.md) |
| RWA lending, real-world asset-backed lending, credit facility, TrueFi-style, Goldfinch-style | [reference/solidity/protocols/rwa-lending.md](reference/solidity/protocols/rwa-lending.md) |

---

## Ethereum/Solidity DeFi AMM/DEX Tricks

- Check if external calls use .call() but don't validate return data length for contracts that might self-destruct
- Look for reentrancy guards that protect state but allow view function calls to manipulated external contracts
- Verify if token transfers assume 18 decimals but interact with tokens having different decimal precision
- Search for oracle price feeds that don't validate if Chainlink aggregator rounds are stale or incomplete
- Check if swap calculations use mulDiv but don't handle intermediate overflow in complex pricing formulas
- Look for MEV extraction opportunities in multi-hop swaps or arbitrage paths
- Verify if slippage protection accounts for fee-on-transfer tokens reducing received amounts

## Ethereum/Solidity Lending/Borrowing Tricks

- Check if liquidation logic handles underwater positions correctly during market crashes
- Look for interest rate calculations that can overflow with extremely high utilization rates
- Verify if collateral valuation uses time-weighted average prices to prevent flash loan manipulation
- Search for repayment functions that don't update borrower's debt correctly with compound interest
- Check if flash loan callbacks don't verify the original caller owns the loan amount
- Look for governance proposals that can execute immediately during timelock by manipulating block.timestamp
- Verify if permit functions check deadline but don't prevent replay attacks across forks

## Cross-chain Bridge Tricks

- Check if message verification validates merkle proofs against correct block headers
- Look for relay systems that don't verify message ordering or prevent replay attacks
- Verify if asset locks on source chain require corresponding unlocks/mints on destination
- Search for validator consensus mechanisms that can be manipulated with <33% stake
- Check if time-locked withdrawals can be front-run during dispute periods
- Look for bridge contracts that don't handle failed transactions or stuck assets
- Verify if cross-chain message passing validates sender authenticity

## NFT/Gaming Protocol Tricks

- Check if metadata URIs can be modified by unauthorized parties after minting
- Look for random number generation using predictable sources (block.timestamp, blockhash)
- Verify if royalty calculations handle edge cases (zero prices, maximum royalties)
- Search for batch operations that don't validate individual item permissions
- Check if game state transitions can be front-run or sandwich attacked
- Look for NFT approvals that don't expire or can be exploited across marketplaces
- Verify if play-to-earn mechanisms have anti-sybil protections

## Governance/DAO Tricks

- Check if voting power calculations can be manipulated through flash loans or delegate loops
- Look for proposal execution that doesn't validate proposal state before execution
- Verify if timelock delays can be bypassed through proposal dependencies or emergency functions
- Search for quorum calculations that don't account for total supply changes
- Check if delegation mechanisms prevent vote buying or circular delegation
- Look for treasury access controls that don't require multi-signature approval
- Verify if proposal cancellation can be abused by proposers or governance attacks

## Security Categories

### Access Control & Upgradeability

- Unauthorized access to sensitive functions
- Insecure constructor/init logic
- Upgradeability pattern misuse (e.g. unprotected upgradeTo)

### Fund Management

- Reentrancy vulnerabilities (single-function, cross-function, cross-contract, read-only)
- Incorrect accounting or balance tracking
- Incorrect token transfers or approvals
- Unchecked external call returns

### DeFi Protocol Logic

- Oracle manipulation vulnerabilities
- Flash loan attack vectors
- Slippage and sandwich attack risks
- Price calculation errors
- Fee-on-transfer token handling

### EVM & Solidity Specifics

- Integer overflow/underflow in older Solidity versions (<0.8.0)
- Timestamp dependencies and block manipulation
- Weak randomness sources
- Front-running vulnerabilities in MEV-sensitive logic

### Contract Logic Integrity

- Incorrect state transitions
- Lack of input validation leading to invariant violation
- Division precision errors
- Denial of service through unbounded operations

## Knowledge Base References

For detailed vulnerability patterns, see:
- `reference/solidity/fv-sol-1-reentrancy/` - Reentrancy attack patterns
- `reference/solidity/fv-sol-2-precision-errors/` - Fixed-point math issues
- `reference/solidity/fv-sol-3-arithmetic-errors/` - Overflow/underflow patterns
- `reference/solidity/fv-sol-4-bad-access-control/` - Access control vulnerabilities
- `reference/solidity/fv-sol-5-logic-errors/` - Business logic flaws
- `reference/solidity/fv-sol-6-unchecked-returns/` - External call validation
- `reference/solidity/fv-sol-7-proxy-insecurities/` - Proxy pattern vulnerabilities
- `reference/solidity/fv-sol-8-slippage/` - MEV and slippage issues
- `reference/solidity/fv-sol-9-unbounded-loops/` - DoS vulnerabilities
- `reference/solidity/fv-sol-10-oracle-manipulation/` - Oracle attack vectors
