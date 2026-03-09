# FV-TON-9-CL3 AMM and Lending

## TLDR

AMM contracts are vulnerable to user-supplied slippage bypass and missing deadlines; lending contracts are vulnerable to insufficient liquidation incentives, bad debt without socialization, and invariant violations after swaps or partial liquidations.

## Detection Heuristics

**Slippage from on-chain state**
- `min_amount_out` calculated from current pool reserves inside the contract rather than supplied by the user in the message body - an attacker can sandwich the transaction and set a favorable slippage floor
- No `min_amount_out` parameter at all - unlimited slippage

**Missing swap deadline**
- Swap operation has no `valid_until` or `deadline` field in the message
- No `throw_unless(error::expired, now <= deadline)` in the swap handler
- Pending swap messages can be held and executed when the price has moved against the user

**AMM invariant not verified**
- After a swap, `reserve_a * reserve_b` (or the equivalent invariant) is not re-checked against the pre-swap value
- LP add/remove does not verify proportional contribution to the pool, allowing one-sided manipulation

**Insufficient liquidation incentive**
- Liquidation bonus is a percentage of the position but minimum position size is not enforced - for small positions, the bonus does not cover TON gas costs, leaving bad positions unliquidated
- Self-liquidation check absent: liquidator == borrower with a positive bonus yields net profit for the borrower

**Bad debt not handled**
- Liquidation can result in debt exceeding collateral value with no insurance fund or bad debt socialization mechanism
- Protocol balance sheet does not track bad debt - eventual withdrawal run when tracked liabilities exceed assets

## False Positives

- Slippage check is done by a router that wraps the swap and enforces the user-supplied minimum - confirm the router's enforcement cannot be bypassed by calling the underlying pool directly
