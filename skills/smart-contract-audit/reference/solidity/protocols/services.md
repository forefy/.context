# DeFi Services Security Patterns

> Applies to: protocol utility services, fee routers, meta-aggregators, keeper networks, automation bots, reward distributors, merkle airdrop distributors

## Protocol Context

DeFi service contracts act as intermediaries—routing trades, bridging chains, distributing rewards, and automating keeper operations—across a wide range of underlying protocols. Unlike single-purpose AMMs or lending pools, service contracts are characterized by broad token and protocol integration surfaces, frequent cross-chain message passing, and reward accounting that must remain correct across arbitrary user behavior and rebalancing events. The combination of untrusted token inputs, multi-step state updates, and cross-chain asynchrony produces a vulnerability surface that rewards systematic, path-by-path analysis rather than single-function review.

---

### Access Control and Privilege Escalation (ref: fv-sol-4)

**Protocol-Specific Preconditions**
- Proxy implementation contracts are not initialized on deployment, allowing any caller to claim ownership and execute `selfdestruct` via delegatecall
- Admin and owner roles are designed as independent checks but one role controls the appointment of the other, undermining separation
- Keeper or operator roles accept unconstrained numerical parameters (reward proportions, fee rates) that can be set to 100% to redirect all funds

**Detection Heuristics**
- Verify that `initialize()` on implementation contracts is protected by `_disableInitializers()` in the constructor
- Check role separation: can one role nominate or dismiss another role without independent governance approval?
- Confirm bounded ranges on all keeper-controllable parameters (reward proportion, slippage tolerance, fee basis points)
- Review whether `renounceOwnership` or equivalent admin removal leaves critical protocol functions permanently inaccessible

**False Positives**
- Admin override is an intentional emergency design with documented safety properties
- Initialization is called atomically within a factory `create` function, eliminating the front-running window
- Access control is enforced by a multi-sig with a known quorum requirement

**Notable Historical Findings**
Biconomy's `SmartAccount` implementation contract was not initialized at deployment, allowing an attacker to call `initialize` on the implementation directly, become its owner, and destroy it via a `selfdestruct` delegatecall—bricking every proxy sharing that implementation. SeaDrop's `onlyOwnerOrAdmin` modifier allowed either the owner or admin to overwrite the other's drop configuration, and because the owner chose the admin at construction time, the supposed independence of the two roles was illusory. Taurus Protocol's keeper received an unchecked `_rewardProportion` parameter, enabling a malicious or compromised keeper to set it to 10000 basis points and direct the entire reward pool to themselves.

**Remediation Notes**
- Call `_disableInitializers()` unconditionally in every upgradeable implementation's constructor
- Require admin appointments to go through a governance vote or timelock independent of the current owner
- Validate all keeper parameters against explicit maximum bounds enforced at the contract level, not just off-chain

---

### Cross-Chain Bridge and Message Validation (ref: fv-sol-5)

**Protocol-Specific Preconditions**
- Cross-chain message receivers do not verify that `msg.sender` is the trusted bridge relayer or that the origin sender matches the expected source chain contract
- `mirrorConnector` or `remoteConnector` variables are permitted to be `address(0)`, silently discarding messages
- Gas limit estimates for destination chain execution are hardcoded or computed incorrectly, causing destination execution to revert and strand tokens
- Bridge-specific chain IDs (Wormhole, LayerZero) differ from EVM `chainId` values and are confused in routing logic

**Detection Heuristics**
- Verify every cross-chain receiver checks both `msg.sender == trustedBridge` and `originSender == trustedRemoteSenders[originChainId]`
- Search for `mirrorConnector == address(0)` reachability; messages sent to the zero address are silently lost
- Audit destination gas estimation logic for dynamic payload-size adjustment, especially on L2s with different gas models
- Confirm a recovery or retry path exists when destination execution fails; tokens must not be permanently stranded in the bridge contract

**False Positives**
- The bridge protocol verifies sender at the transport layer, making application-layer checks redundant by design
- A dedicated retry/recovery mechanism handles all failed destination executions
- The protocol targets a single, well-tested chain pair with validated gas parameters

**Notable Historical Findings**
Connext contained multiple connector contracts where `mirrorConnector` was never validated for zero-address, causing `processMessage` to silently discard all messages routed through those connectors. LI.FI's `GenericBridgeFacet` accepted user-supplied destination call data with insufficient validation, allowing an attacker to craft calls that triggered `transferFrom` on approved tokens held in the Executor contract. Holograph's `LayerZeroModule` miscalculated destination gas by a significant factor, causing cross-chain NFT operations to fail on arrival and permanently lock assets when no recovery path was provided.

**Remediation Notes**
- Require `connector != address(0)` before dispatching any cross-chain message
- Implement a `failedMessages` mapping with a retry or refund path for any destination execution that reverts
- Use bridge-specific chain ID registries and validate them independently from EVM `block.chainid`

---

### Fee-on-Transfer Token Incompatibility (ref: fv-sol-5)

**Protocol-Specific Preconditions**
- Service contracts route or aggregate arbitrary user-supplied ERC-20 tokens without restricting to a known-safe whitelist
- Internal accounting increments a balance mapping by the declared transfer amount immediately after `transferFrom`, without measuring actual receipt
- Callback-based token intake patterns (e.g., `timeswapMintCallback`) verify exact amounts arrived, causing hard reverts for any fee-bearing token

**Detection Heuristics**
- Find all `transferFrom(sender, address(this), amount)` calls followed by `balances[user] += amount` or equivalent; flag the lack of before/after balance measurement
- Identify `require(token.balanceOf(address(this)) >= before + exactAmount)` patterns that break for fee-bearing tokens
- Check protocol documentation: if it claims to support "any ERC-20," treat this as a fee-on-transfer vulnerability indicator
- Look for rebasing token interactions where `balanceOf` can change between operations without an explicit transfer

**False Positives**
- Protocol explicitly whitelists non-fee tokens and reverts on unsupported inputs
- Protocol wraps rebasing tokens into non-rebasing equivalents (e.g., wstETH) at ingress
- Balance-difference pattern is already implemented throughout

**Notable Historical Findings**
Trader Joe's liquidity contract allowed a user to transfer tokens to themselves, which triggered the fee-on-transfer deduction while crediting the full nominal amount, net-inflating their own balance by the fee amount on every self-transfer. Beanstalk's internal balance system credited users the full declared amount from `LibTransfer`, but the protocol's actual token balance was systematically short by the accumulated transfer fees across all deposits, eventually causing insolvency in the affected token pools. Connext explicitly acknowledged fee-on-transfer tokens as unsupported but did not enforce this restriction at the smart contract level, leaving the swap path open to economically harmful inputs.

**Remediation Notes**
- Measure received amount as `token.balanceOf(address(this)) - balanceBefore` for every token intake
- Optionally, add a strict mode: `require(actualReceived == amount, "Fee-on-transfer not supported")` at service contract ingress
- Document and enforce the supported token list via an allowlist contract rather than relying on documentation alone

---

### First Depositor Vault Share Inflation (ref: fv-sol-5)

**Protocol-Specific Preconditions**
- Share-based vault uses `shares = assets * totalSupply / totalAssets` where `totalAssets` is derived from `balanceOf(address(this))`
- A first depositor can mint one share for one wei, then inflate `balanceOf` by donating tokens, causing all subsequent depositors to receive zero shares
- No minimum initial deposit, dead share mechanism, or virtual offset is enforced at initialization

**Detection Heuristics**
- Identify vault contracts minting shares proportional to `deposit * totalSupply / balanceOf(address(this))`
- Verify first-deposit path cannot create fewer than a configurable minimum share count
- Confirm `balanceOf` cannot be inflated by direct token transfers that bypass the vault's internal accounting
- Check whether zero-shares output is handled; if `shares == 0` is not rejected, victim deposits are silently absorbed

**False Positives**
- Virtual shares offset (e.g., OpenZeppelin ERC4626 `_decimalsOffset`) is implemented
- Dead shares are burned on first deposit, preventing manipulation of the exchange rate
- Vault uses an internal balance tracker that ignores direct token donations

**Notable Historical Findings**
Surge Finance's first depositor could deposit one wei, receive one share, then donate enough tokens to inflate the vault's asset balance such that the next depositor's large deposit minted zero shares—the entire deposit being absorbed by the one-share holder. Liquid Collective's share minting was vulnerable to front-running: an attacker donating one wei to the contract before the first legitimate deposit caused the legitimate depositor to receive zero shares, effectively stealing the entire deposit. Caviar's AMM pool initialization had a related variant where the first depositor could set an extreme price ratio with a negligible liquidity commitment.

**Remediation Notes**
- Burn a configurable amount of dead shares to `address(0xdead)` on first deposit to anchor the exchange rate
- Track internal asset balances separately from `balanceOf(address(this))` so donations do not affect share pricing
- Enforce a minimum initial deposit that makes economic manipulation unprofitable

---

### Flash Loan Price Manipulation (ref: fv-sol-10)

**Protocol-Specific Preconditions**
- Collateral valuation uses `balanceOf`, `totalAssets / totalSupply`, or AMM `getReserves` within the same transaction context as the collateral check
- ERC-4626 vault share price is read spot for collateral or liquidation decisions
- Checkpoint-based voting uses current balance, allowing flash-borrowed tokens to inflate vote weight within a single block

**Detection Heuristics**
- Confirm no price or collateral calculation reads `balanceOf` or `getReserves` in the same transaction context without a multi-block averaging mechanism
- Verify flash-loan guard patterns: `require(lastDepositBlock[msg.sender] < block.number)` before any borrow or vote action
- Check ERC-4626 oracle implementations for spot-price reads on `totalAssets / totalSupply`
- Audit Balancer vault integrations for read-only reentrancy windows during join/exit callbacks where spot reserves are stale

**False Positives**
- Chainlink or other off-chain oracle is used exclusively and is immune to same-block manipulation
- TWAP window of 30+ minutes is used for all price reads
- Flash-loan guard prevents same-block deposit-and-action sequences
- Economic manipulation cost exceeds potential gain due to deep liquidity

**Notable Historical Findings**
Telcoin allowed staking and unstaking in the same block with no guard, enabling an attacker to flash-borrow TEL, stake a large amount to inflate snapshot weight, collect inflated rewards, and repay the flash loan in a single transaction. Sentiment's ERC4626Oracle read `totalAssets / totalSupply` spot for collateral valuation; a flash loan donation to the underlying vault could inflate this ratio and allow over-borrowing. Carapace Protocol's protection-seller withdrawal mechanism could be bypassed by a flash-loan-assisted Sybil on withdrawal requests, allowing manipulation of the leverage factor governing how much capital could be withdrawn in a single epoch.

**Remediation Notes**
- Require at least one block between deposit and any privileged action (borrow, vote, redemption)
- Use a 30-minute Uniswap V3 TWAP via `OracleLibrary.consult` rather than spot reserves for all collateral pricing
- For ERC-4626 vaults used as collateral, compute share price using a TWAP snapshot of `totalAssets / totalSupply` rather than the current block value

---

### Front-Running and Sandwich Attacks (ref: fv-sol-8)

**Protocol-Specific Preconditions**
- Swap or meta-aggregation functions lack `minAmountOut` or `deadline` parameters, enabling MEV sandwich extraction
- `approve()` pattern allows a spender to spend the old allowance before a reduction transaction lands
- Keeper automation functions executing on-chain swaps do not enforce slippage protection, allowing sequencer or block-builder manipulation
- Blacklist addition functions are observable in the mempool, giving targets time to move funds before the restriction takes effect

**Detection Heuristics**
- Confirm every swap entry point accepts and enforces both `minAmountOut` and a `deadline` timestamp
- Search for `token.approve(spender, amount)` patterns and replace with `increaseAllowance`/`decreaseAllowance` or `forceApprove` + reset
- Check keeper-triggered swaps for hardcoded zero slippage tolerance or missing slippage parameters
- Identify blacklist or role-revocation functions and assess whether the target can front-run to move assets or delegate authority

**False Positives**
- Slippage protection is enforced by the calling context (e.g., user-facing wrapper always sets `minAmountOut`)
- Commit-reveal scheme prevents value extraction from pending transactions
- Flashbots or private mempool makes front-running economically infeasible for the deployment chain

**Notable Historical Findings**
Connext's `SponsorVault` used a spot DEX price to compute reimbursements, enabling a sandwicher to inflate the price between the sponsorship calculation and the actual swap execution. Tigris Trade allowed riskless trades by exploiting a delay check that could be bypassed: users observed pending price-sensitive transactions and submitted their own trades with precisely calibrated timing to capture the spread risk-free. Liquid Collective's `approve()` function directly overwrote allowances, enabling the classic front-run: a spender who observed a reduction transaction could spend the full original allowance before the reduction landed and then spend again under the new allowance.

**Remediation Notes**
- Add `uint256 minAmountOut` and `uint256 deadline` to every swap function signature and enforce both
- Use `SafeERC20.forceApprove(spender, 0)` followed by `forceApprove(spender, amount)` for all approval sequences
- For keeper swaps, accept a caller-provided slippage bound and revert if the swap output falls below it

---

### Oracle Stale Price and Manipulation (ref: fv-sol-10)

**Protocol-Specific Preconditions**
- `latestAnswer()` (deprecated Chainlink function) is used without round metadata
- `latestRoundData()` is called but `answeredInRound >= roundId` and `block.timestamp - updatedAt < STALENESS` checks are omitted
- Chainlink `minAnswer`/`maxAnswer` circuit breaker bounds are cached at construction time as immutables; if Chainlink updates the aggregator, the cached bounds become stale
- L2 deployments on Arbitrum or Optimism do not check the Sequencer Uptime Feed before trusting price data

**Detection Heuristics**
- Search for `latestAnswer()` usage; it must be replaced with `latestRoundData()` with full validation
- For every `latestRoundData()` call, verify all five return values: `roundId`, `price > 0`, `updatedAt > 0`, `block.timestamp - updatedAt < heartbeat`, `answeredInRound >= roundId`
- Check if aggregator min/max bounds are stored as immutables versus fetched dynamically from the current aggregator address
- On L2 deployments, confirm the Sequencer Uptime Feed is consulted and a grace period is enforced before trusting price data

**False Positives**
- Oracle is used only for non-critical display purposes with no downstream financial effects
- Protocol explicitly pauses all operations when oracle returns a stale price, preventing any financial action on bad data
- Multiple independent oracle sources are aggregated and a stale reading from one is overridden by others

**Notable Historical Findings**
Float Capital's entire market malfunctioned when a gap in Chainlink's update frequency caused `latestAnswer()` to return a value outside the expected range without the contract detecting it as stale, triggering cascading incorrect position valuations. Sentiment's WSTETH-ETH Curve LP token oracle relied on a spot Curve price that was manipulated via a flash loan, causing incorrect liquidations and undercollateralized borrowing simultaneously. Morpho cached a P2P rate snapshot that could diverge significantly from the live on-chain rate when the underlying Compound or Aave protocol updated its indexes between Morpho's own updates.

**Remediation Notes**
- Validate all five return values of `latestRoundData()` on every call; create a shared internal validation function to avoid copy-paste omissions
- Fetch `aggregator.minAnswer()` and `aggregator.maxAnswer()` dynamically rather than caching them as immutable constructor values
- For L2 deployments, add a required `sequencerUptimeFeed` check with a configurable grace period (minimum 3600 seconds)

---

### Reentrancy (ref: fv-sol-1)

**Protocol-Specific Preconditions**
- Service contracts interact with Balancer vault join/exit callbacks, creating read-only reentrancy windows where the contract's internal reserve state is temporarily inconsistent
- ERC-777 tokens with `tokensReceived` hooks are accepted as deposit or collateral assets
- Reward distribution functions send ETH or call external protocol contracts before marking user positions as processed
- Reentrancy guard is applied to one entry point but another entry point shares the same state without a guard

**Detection Heuristics**
- Identify all external calls: `call`, `send`, `transfer`, `safeTransfer`, `safeTransferFrom`, and any integration with Balancer, ERC-777, or ERC-1155
- Check for state variable writes after external calls in every function and callgraph
- For read-only reentrancy: verify that view functions reading reserve or balance state are not callable from external protocols during a Balancer join/exit callback
- Confirm `nonReentrant` covers all entry points that access the same shared state, not just individual functions

**False Positives**
- External call target is a trusted, immutable contract known to have no callbacks
- Strict CEI is followed throughout and all state is finalized before any external call
- `nonReentrant` covers all entry points that share the affected state
- Token is a standard ERC-20 with no transfer hooks

**Notable Historical Findings**
Notional Finance's `redeemNative` function performed an external transfer before updating the internal redemption state, allowing repeated reentrancy that permanently froze fund access and caused systematic misaccounting. Stakehouse Protocol had multiple reentrancy paths in its reward distribution functions: `_distributeETHRewardsToUserForToken` sent ETH before marking the user's share as distributed, while `withdrawETH` decremented `idleETH` before burning the receipt token, in opposite order of what was needed. Cron Finance was vulnerable to Balancer read-only reentrancy: an external pricing function read virtual reserves during a Balancer join callback when the pool's state was temporarily inconsistent, producing manipulable price reads.

**Remediation Notes**
- Apply `nonReentrant` to every function that modifies shared accounting state
- Add a `_reentrancyGuardEntered()` check to view functions used as price oracles to prevent read-only reentrancy
- Strictly follow CEI: finalize all internal state (balance decrements, supply updates, claim flags) before any external call

---

### Reward Distribution Accounting Errors (ref: fv-sol-5)

**Protocol-Specific Preconditions**
- Cached reward variables are set but never reset to zero after a claim, allowing infinite re-claiming
- Unstake logic deletes the total pool's share count instead of the user's individual share count
- Reward token removal makes all unclaimed balances irretrievable without a grace period for existing stakers
- Reward accumulator (`rewardPerToken`) is not updated atomically before each stake/unstake operation

**Detection Heuristics**
- Verify reward accumulator is updated as the first operation in every `stake`, `unstake`, `deposit`, and `withdraw` function
- Check `cachedUserRewards` or equivalent variables: are they reset to zero after a successful claim?
- Trace `unstake` logic to confirm it decrements `userShares[user]`, not `totalShares` or `poolShares`
- Audit reward token removal paths for unclaimed balance accessibility after removal

**False Positives**
- Cached rewards are intentionally persistent as part of a vesting schedule
- Reward token removal is preceded by a mandatory governance-controlled grace period
- "Total shares" deletion is intentional in an epoch-based reset system

**Notable Historical Findings**
OlympusDAO's `cachedUserRewards` was incremented on withdrawal but never reset after a claim call, allowing users to claim the same accumulated rewards indefinitely until the contract was drained. Stakehouse Protocol's unstake function read `_rewardPoolShares[poolId][cycleId]` (the total for the pool) and deleted the entire mapping entry, zeroing out every other user's share in that cycle in a single operation. Neo Tokyo's staking contract updated a pool's total points without adjusting existing stake positions' debt offsets, causing all currently staked positions to immediately over-claim on their next interaction.

**Remediation Notes**
- Zero `cachedUserRewards` atomically within the claim function, not in a separate cleanup step
- Explicitly use `userShares[user]` as the subtrahend in unstake logic, never the pool-wide accumulator
- Before removing a reward token, snapshot all unclaimed balances and maintain claimability for a minimum grace period (e.g., 30 days)

---

### Rounding and Precision Loss (ref: fv-sol-2)

**Protocol-Specific Preconditions**
- Service contract aggregates or routes between tokens with heterogeneous decimals (USDC at 6, WETH at 18), and a single `1e18` divisor is applied to both
- Division precedes multiplication in share or rate calculations, truncating intermediate results
- Reward-per-token accumulator uses insufficient precision for small reward rates over large staked amounts, rounding to zero per update

**Detection Heuristics**
- Search for division operations followed by multiplication in the same expression
- Identify hardcoded `1e18` divisors applied to token amounts without checking whether the token has 18 decimals
- Check reward accumulator update frequency: does `reward / totalStaked` round to zero for the expected reward rates?
- Look for `priceFeed.decimals()` return values that are used in scaling calculations and verify the math handles all realistic decimal values

**False Positives**
- Precision loss is bounded to sub-cent dust values with no amplification vector
- Protocol explicitly rounds in the protocol's favor and the per-user loss is negligible
- `mulDiv` or equivalent full-precision arithmetic is used throughout

**Notable Historical Findings**
Surge Finance's `userCollateralRatioMantissa` calculation used token pairs with different decimals and a single fixed-precision divisor, producing ratios that were systematically incorrect for pairs involving USDC or WBTC—causing liquidations to trigger at wrong thresholds. Taurus Protocol assumed 18-decimal collateral throughout its pricing and leverage calculations, making the protocol entirely non-functional for tokens like WBTC, USDC, or USDT. Liquid Collective's operator reward shares suffered from compounding division errors due to multiple sequential divisions rather than a single `mulDiv` operation, causing measurable under-distribution to node operators over time.

**Remediation Notes**
- Always multiply before dividing: `(amount * PRECISION) / price` rather than `(amount / price) * PRECISION`
- Normalize all token amounts to a common 18-decimal representation at ingress using `amount * 10**(18 - tokenDecimals)`
- Use `1e36` precision for reward-per-token accumulators to prevent rounding to zero on small emission rates

---

### Signature and Message Replay Attacks (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- EIP-4337 UserOperation hash does not include `chainId`, making the same user operation valid on any EVM chain
- EIP-712 domain separator is computed once in the constructor with `block.chainid` as an immutable; after a hard fork, the cached separator becomes valid on both chains
- Merkle proof-based minting or airdrop claiming lacks per-address claim tracking, allowing proofs to be reused in the same epoch

**Detection Heuristics**
- Verify all `ecrecover` / `ECDSA.recover` call sites include `block.chainid` or a domain separator computed dynamically
- Search for `immutable DOMAIN_SEPARATOR` computed in the constructor; this breaks after hard forks
- For Merkle airdrop contracts, confirm a `claimed[address]` or `claimedBitmap` prevents proof reuse
- Validate that `ecrecover` return value is checked against `address(0)` before use

**False Positives**
- Protocol deploys to a single chain with no fork risk and the domain separator is documented as chain-specific
- Per-address mint caps effectively prevent economically significant replay even without explicit digest tracking
- Domain separator is recomputed dynamically using `block.chainid` on every call

**Notable Historical Findings**
Biconomy's paymaster hash omitted `chainId`, allowing a UserOperation signed for one chain to be replayed on any other EVM chain the paymaster was deployed to. Golom discovered that its EIP-712 domain separator was fixed at construction time with the deployment chain's ID; after an ETH hard fork, the stored separator remained valid on both the original and forked chain, enabling cross-chain replay of any signed order. SeaDrop's `mintSigned` function did not track used signatures, allowing a valid signed mint allocation to be submitted repeatedly until the per-wallet cap was reached, but the cap itself could be bypassed by using separate wallets.

**Remediation Notes**
- Compute the EIP-712 domain separator dynamically in a view function using `block.chainid` rather than storing it as an immutable
- Track all used signature digests in a `mapping(bytes32 => bool) public usedSignatures` regardless of nonce-based replay protection
- For UserOperation-style hashes, follow EIP-4337 exactly by including `chainId` in the packed encoding

---

### State Desynchronization and Missing State Updates (ref: fv-sol-5)

**Protocol-Specific Preconditions**
- Asset recovery functions (`bringUnusedETHBack`, `rescueTokens`) move ETH or tokens into the contract without updating the corresponding internal tracking variable (`idleETH`, `totalAssets`)
- Liquidations executed on external lending protocols seize collateral without the service contract updating its internal position records
- Reward checkpoint logic overwrites `claimed` to the current maximum value without first distributing the pending amount to the user

**Detection Heuristics**
- For every function that changes the contract's real token or ETH balance, verify a corresponding internal variable is incremented or decremented in the same transaction
- Search for `delete` or direct assignment to balance/position tracking variables where `+=` / `-=` should be used
- Check all deposit/withdraw hooks for completeness: do they update reward state, checkpoint values, and balance trackers atomically?
- Audit config update functions for failing to account for already-accrued values before resetting the config variable

**False Positives**
- The "missing update" variable has no downstream financial effects within the protocol
- State is reconciled in a subsequent mandatory call that always precedes the next exploitable action
- The function is admin-only and manual reconciliation is an accepted operational procedure

**Notable Historical Findings**
Stakehouse Protocol's `bringUnusedETHBackIntoGiantPool` transferred ETH from staking vaults back to the giant pool but never incremented `idleETH`, causing subsequent deposit/withdrawal operations to use a stale (lower) idle balance and systematically underpay users. OlympusDAO's withdrawal logic set `userRewardDebts` to zero before computing the debt difference, ensuring the full accumulator value was credited rather than only the delta—a single off-by-one in the order of operations that allowed unlimited reward extraction. Morpho's state desynchronized from Aave's when an Aave-level liquidation seized a user's collateral without Morpho's internal accounting being notified, leaving phantom collateral recorded in Morpho's books.

**Remediation Notes**
- Measure balance change as `after - before` on every asset recovery operation and add the delta to the internal tracker
- In reward checkpoint logic, always distribute pending rewards to the user before overwriting the `claimed` checkpoint
- For protocols that integrate external lending, implement a reconciliation function that reads the external protocol's current state and syncs internal records

---

### Unsafe ERC20 Approval Patterns (ref: fv-sol-6)

**Protocol-Specific Preconditions**
- Service contract calls `token.approve(router, amount)` without first resetting to zero; USDT and similar tokens revert on non-zero to non-zero approval
- Router or bridge address in the approval is user-controlled, allowing an attacker to approve their own contract and drain the service contract's token balance
- Max approvals (`type(uint256).max`) are granted to upgradeable routers that may change behavior after the approval is set

**Detection Heuristics**
- Search for `IERC20.approve(spender, nonZeroAmount)` without a preceding `approve(spender, 0)` or equivalent `forceApprove`
- Verify the approved spender is a hardcoded, immutable, audited address—not a user-supplied or governance-updatable parameter
- Check for `type(uint256).max` approvals to external contracts; confirm the contract is immutable or the approval is revoked after use
- Identify patterns where the same approval is granted in a loop without revocation between iterations

**False Positives**
- The token is known to not require zero-reset (standard OpenZeppelin ERC-20)
- Allowance is always fully consumed in the same transaction, leaving no residual
- Spender is a hardcoded, immutable, well-audited address

**Notable Historical Findings**
UXD Protocol's `PerpDepository.rebalance` approved `PerpDepository` for user token spending with no validation of who triggered it, allowing any user who had previously approved the depository to have their entire balance drained by a third-party caller. LI.FI's facets approved arbitrary user-supplied addresses for ERC-20 tokens held by the diamond proxy, enabling token theft by routing through a malicious "facet" address. Notional's approval sequence failed to reset to zero before setting a new allowance, causing all swaps to revert permanently on USDT-style tokens that enforce the zero-reset requirement.

**Remediation Notes**
- Use `SafeERC20.forceApprove(spender, amount)` which handles the zero-reset automatically
- Never accept a spender address as a user-supplied parameter; hardcode or restrict to a registry of audited contracts
- Revoke approvals (`forceApprove(spender, 0)`) immediately after single-use operations rather than relying on exact consumption
