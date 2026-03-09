# FV-ANC-12-CL3 Flash Loan Oracle Price Manipulation

## TLDR

On-chain Solana programs that derive prices from AMM pool reserves or spot ratios rather than time-weighted or off-chain oracle feeds can be manipulated within a single transaction using flash loans. An attacker borrows a large amount, moves the pool price, executes the target operation at the manipulated price, then reverses the price and repays the loan, all within one atomic transaction.

## Detection Heuristics

**Spot Price Derived From Pool Reserves**
- Price computed as `token_a_reserve / token_b_reserve` directly from a pool account at instruction execution time
- No TWAP (time-weighted average price) or multi-block averaging used; price reflects the instantaneous reserve ratio
- Protocol integrates with an AMM pool but does not use the AMM's TWAP oracle account; reads only the vault token balances

**Flash Loan Integration Without Price Guard**
- Protocol accepts flash loans and does not mark positions or prices as "flash-loan-active" to prevent borrowers from using the borrowed liquidity to move prices
- Liquidation or collateral valuation uses the same price source as the flash loan target pool, allowing a borrower to manipulate both simultaneously

**No Price Deviation Check**
- New transaction's price not compared against a recent historical price stored on-chain; no maximum allowable price movement per block
- Protocol does not require a minimum number of slots to pass between price-sensitive operations, allowing rapid repeated manipulation

## False Positives

- Protocol uses Pyth or Switchboard off-chain oracle feeds with staleness checks; these are not manipulable via on-chain flash loans
- Protocol uses the AMM's official TWAP oracle account with a sufficiently long window that flash loan manipulation within one block cannot significantly move the average
