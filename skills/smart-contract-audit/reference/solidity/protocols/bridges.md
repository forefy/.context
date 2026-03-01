# Bridge and Cross-Chain Security Patterns

> Applies to: asset bridges, token bridges, cross-chain message passing, LayerZero integrations, Wormhole integrations, Axelar integrations, lock-and-mint bridges, burn-and-mint bridges, optimistic bridges

## Protocol Context

Bridges are architecturally unique because correctness depends on two independent execution environments that cannot atomically read each other's state: a lock or burn on the source chain must be faithfully reflected as a mint or release on the destination chain with no shared transaction context to enforce atomicity. The trust model extends beyond on-chain code to off-chain relayers, oracle sets, or validator committees whose compromise can authorize fraudulent minting without corresponding locking. Every cross-chain message carries a distinct attack surface — replay across chains, payload tampering during transmission, and gas griefing on the destination side — that has no equivalent in single-chain protocols.

## Bug Classes

### Access Control Misconfiguration (ref: fv-sol-4)

**Protocol-Specific Preconditions**
- Critical bridge functions (router recipient setter, fee recipient, mirror connector address) lack access control modifiers or use one-time-set patterns vulnerable to front-running
- Privileged roles such as admin or operator can unilaterally change bridge parameters (acceptance delay, stable swap address, flow rate) or drain router liquidity
- Ownership renouncement or transfer to the zero address removes the only actor capable of performing emergency actions, permanently bricking bridge operations
- Role assignment for multisig participants lacks a removal path, leaving compromised signers permanently privileged

**Detection Heuristics**
1. Enumerate every `external` and `public` function that writes state; verify each has an appropriate access control modifier
2. Check one-time-set patterns for front-run exposure: any setter that checks `if (value == address(0))` rather than `if (msg.sender == deployer)` is vulnerable
3. Confirm every privileged role can be revoked and that revocation does not orphan protocol functionality
4. Verify ownership transfer uses the two-step nominate-then-accept pattern
5. Audit diamond facets: `diamondCut` allowing re-execution of already-applied cuts is a distinct access control failure

**False Positives**
- Intentionally permissionless functions (public liquidations, permissionless relayer calls)
- Admin functions protected by a multi-sig with a timelock
- Setters that affect only the calling account's own state

**Notable Historical Findings**
In Connext audits, multiple findings documented that the `WatcherManager`, router recipient, and `acceptanceDelay` could be configured by unauthorized actors or configured only once with no removal path, leaving the bridge in an irreparable state after a misconfiguration. The Decent bridge allowed anyone to overwrite the router address in the `DcntEth` contract, enabling immediate fund theft at zero cost. Axelar's multisig implementation allowed the same proposal to be executed repeatedly due to missing deduplication, and a deployer wallet retained the ability to spoof validated senders after an ownership transfer completed.

**Remediation Notes**
One-time-set bridge parameters must be protected by the deployer address stored at construction time, not by checking whether the parameter is already populated. All bridge admin roles must support removal, and any removal path must be tested for cascading impact on live routes. Ownership transfers must use the nominate-and-accept pattern so that a mis-typed address does not permanently lock administration.

---

### Reentrancy (ref: fv-sol-1)

**Protocol-Specific Preconditions**
- Token transfer callbacks (ERC-777 `tokensReceived`, ERC-721 `safeTransfer`, native ETH `receive`) fire before bridge accounting is finalized
- Bridge executor or router contracts perform external calls to user-specified targets that can re-enter the same function
- Read-only reentrancy: a bridge pricing function reads pool balances (Balancer, Uniswap) during a vault callback, yielding a stale or manipulated price
- Gnosis Safe module hooks (`checkTransaction`, `checkAfterExecution`) can be re-entered before the module's own state is consistent

**Detection Heuristics**
1. Identify all functions that make external calls; confirm state updates precede the call (Checks-Effects-Interactions)
2. Flag any function lacking `nonReentrant` that transfers tokens or calls user-supplied targets
3. Check for ERC-777 token support and whether `tokensReceived` hooks can re-enter deposit or withdraw paths
4. Identify view functions that query on-chain AMM state; determine whether that state can be manipulated inside a callback from the same transaction

**False Positives**
- External calls to immutable, trusted contracts with no callbacks
- Functions where all state updates provably precede external calls and no re-entrant path exists back to the function

**Notable Historical Findings**
Axelar ITS allowed `expressReceiveToken` to be re-entered via ERC-777 token hooks, enabling double-minting of bridged tokens without a corresponding lock on the source side. The Connext Executor's forwarding of user-supplied calldata could re-enter bridge logic before the delivered tokens were marked as claimed. Balancer read-only reentrancy was demonstrated in the Cron Finance audit, where a pricing function could be called during a Balancer vault callback, returning pool balances that were mid-modification.

**Remediation Notes**
Bridge executor and router contracts that forward arbitrary calldata must apply `nonReentrant` regardless of apparent CEI compliance, because the payload target is untrusted. Contracts pricing assets via AMM pool balances should call the Balancer vault reentrancy guard or use a TWAP source that does not read live pool state.

---

### Arithmetic and Precision Errors (ref: fv-sol-2, fv-sol-3)

**Protocol-Specific Preconditions**
- Bridges move tokens between chains with differing decimal precision (e.g., USDC uses 6 decimals on Ethereum, 18 on some L2 deployments); arithmetic that assumes a fixed decimal count silently misprices amounts
- Fee and exchange rate calculations apply division before multiplication, creating compounding precision loss at scale
- `unchecked` arithmetic in packed storage or reward accumulators can silently overflow between claims, causing permanent fund loss
- Collateral valuations compare amounts denominated in different decimal bases without normalization
- Rounding direction is inconsistent with the protocol safety invariant; rounding in the user's favor on withdrawals drains the vault over time

**Detection Heuristics**
1. Check every division that precedes a multiplication in fee, reward, or exchange rate calculations
2. Audit all `unchecked` blocks for overflow potential when values originate from user input or cross-chain messages
3. Verify that token arithmetic normalizes to a common decimal base before comparison or aggregation
4. Confirm oracle price scaling (typically 1e8 for Chainlink) is applied consistently relative to token decimals
5. Confirm rounding direction: shares-to-assets conversions should round against the redeemer; assets-to-shares should round against the depositor

**False Positives**
- `unchecked` blocks used for counter increments where overflow is geometrically impossible given supply constraints
- Precision loss documented as accepted and economically negligible at the protocol's minimum transfer size
- Intentional rounding direction documented in the specification

**Notable Historical Findings**
Connext audits found that `_slippageTol` was evaluated on incomparable scales because it was not adjusted for decimal differences between paired tokens. Axelar ITS had completely broken balance tracking for tokens with different decimal counts on different chains, leading to systematic under-crediting on destination chains. In the Blueberry audit, `IchiLpOracle` returned inflated prices due to a decimal precision error in the price calculation path, causing affected collateral to be valued far above market rate.

**Remediation Notes**
Bridge code that interacts with tokens on multiple chains must never assume a fixed decimal count. All cross-chain accounting should normalize amounts to an internal representation (18-decimal WAD) immediately upon receipt and denormalize only when transferring to the destination token contract. Use `Math.mulDiv` with an explicit rounding direction constant rather than bare division.

---

### Unchecked Return Values (ref: fv-sol-6)

**Protocol-Specific Preconditions**
- Bridge contracts use low-level `.call()` to forward execution or send ETH without asserting the returned success flag
- ERC20 `transfer` and `transferFrom` are called directly without `SafeERC20`, silently succeeding on tokens that return `false`
- A `require(success)` check appears after a `return` statement, making it dead code
- External protocol calls (staking, yield vault withdrawals) return a boolean that is discarded

**Detection Heuristics**
1. Grep for `.call{value:` patterns; confirm every returned `bool` is asserted in a `require` or conditional
2. Find all `IERC20(token).transfer(` and `IERC20(token).transferFrom(` usages; flag any not wrapped in `SafeERC20`
3. Look for `return` statements followed by `require` statements in the same function scope
4. Audit protocol-specific external calls (staking, vault deposit/withdraw) for discarded boolean returns

**False Positives**
- Contracts using `SafeERC20` throughout, which internalizes return value handling
- Fire-and-forget refund attempts where failure is intentionally non-blocking and documented

**Notable Historical Findings**
LI.FI had a finding where the return value of a low-level `.call()` was never checked in the receiver contract, allowing a failed bridge execution to silently pass without delivering funds. In the Sturdy audit, the success check for an ETH withdrawal was placed after a `return` statement and was therefore unreachable, meaning a failed transfer would be treated as successful. Notional finance audits found that `auraBooster.deposit` and `auraRewardPool.withdrawAndUnwrap` returned booleans that were never inspected, leaving failed staking operations undetected and bridge accounting incorrect.

**Remediation Notes**
Every `.call()` that sends ETH in a bridge context must check the success flag; failed delivery should emit an event and queue a retry rather than silently proceeding. Use `SafeERC20` without exception for all ERC20 interactions in bridge contracts, which must handle arbitrary tokens including those that return `false` rather than reverting.

---

### Slippage and Price Manipulation (ref: fv-sol-8)

**Protocol-Specific Preconditions**
- Destination-chain swap legs in bridge transactions do not accept a user-specified `minAmountOut`, forcing users to accept any resulting price
- Cross-chain swap calls use `block.timestamp` as the deadline, which is always satisfied and provides no MEV protection
- The same `slippageTol` parameter is applied to two distinct swaps with different token denominations, making the check incorrect for at least one
- Spot prices from AMM reserves (`getReserves()`) are used for fee or collateral valuation without TWAP protection
- Bridge liquidity operations omit minimum amount parameters

**Detection Heuristics**
1. Find all DEX router calls and check whether `amountOutMin` is 0 or hardcoded to a constant
2. Identify `block.timestamp` used as the `deadline` parameter in any swap call
3. Check bridge functions that execute swaps on the destination side for user-configurable slippage
4. Look for `getReserves()` or `balanceOf`-derived pricing in fee or collateral valuation logic
5. Verify every swap parameter that can be sandwiched is either user-specified or derived from a manipulation-resistant oracle

**False Positives**
- Atomic arbitrage within a single transaction where price is guaranteed by construction
- Admin-controlled rebalancing routed via private mempool with off-chain slippage enforcement
- Functions where a separate oracle-derived check independently enforces minimum output

**Notable Historical Findings**
Connext audits documented that users were forced to accept any slippage on the destination chain because `xcall` offered no mechanism for the initiating user to specify a destination-side minimum output, and separately that `SponsorVault` used an AMM spot price for fee calculation, making it directly exploitable via sandwich attack. WooFi's cross-chain router was found not to correctly enforce slippage in `crossSwap`, allowing large cross-chain swaps to receive heavily discounted outputs. The Juicebox protocol audit found that a delegate architecture forced callers to set zero slippage with no override mechanism.

**Remediation Notes**
Bridge interfaces must accept a user-specified `minAmountOut` and `deadline` for any swap executed on the destination side, even when the swap is performed by a relayer on the user's behalf. Any pricing derived from on-chain AMM state must be validated against a Chainlink or TWAP oracle with an acceptable deviation bound before being used in bridge fee or collateral calculations.

---

### Denial of Service and Gas Griefing (ref: fv-sol-9)

**Protocol-Specific Preconditions**
- Withdrawal queues are activated globally when any single transfer exceeds the flow rate limit, allowing an attacker to delay all bridge withdrawals at minimal cost
- Cross-chain message handlers (`lzReceive`, Connext `execute`) can be fed malicious calldata that causes an unrecoverable revert, permanently blocking the message channel
- Unbounded loops over pending withdrawals or inbound message roots exceed the block gas limit as arrays grow
- Gnosis Safe threshold updates can be triggered to exceed the count of valid signers, bricking the multisig guard

**Detection Heuristics**
1. Identify all flow rate or withdrawal queue mechanisms; check whether activation is global or per-token and per-user
2. Examine cross-chain message handler callbacks for unbounded gas cost or revert paths with no recovery mechanism
3. Find loops over dynamic arrays that grow with protocol usage; confirm they are paginated or bounded by a constant
4. Calculate the cost for an attacker to activate the rate limit versus the damage inflicted on legitimate users

**False Positives**
- Global rate limiting serving as an intentional circuit breaker with a documented governance override path
- Loops bounded by a small configuration constant that cannot be inflated by user action
- Message handlers that use try/catch to isolate per-message failures without blocking the channel

**Notable Historical Findings**
Immutable's bridge had a flow rate check that activated a global withdrawal queue, meaning a single attacker transaction slightly above the threshold would delay every pending withdrawal across all users and tokens. Axelar ITS had two separate high-severity DoS findings: one where the bridge could be blocked by initializing an ITSHub balance for a wrong chain, and another where bridging to a chain with no deployed interchain token caused a permanent DoS on that route. Holograph found a critical issue where an operator could set a destination gas limit above the destination chain's block gas limit, permanently preventing message execution.

**Remediation Notes**
Flow rate limits must be tracked and enforced per-token; activation of a queue for one token must not affect withdrawals of other tokens. Cross-chain message handlers must use try/catch with a stored-payload retry mechanism so that a failed individual message does not block the entire channel. Withdrawal loops must be paginated with an explicit batch size parameter enforced at the call site.

---

### Oracle and Price Feed Issues (ref: fv-sol-10)

**Protocol-Specific Preconditions**
- Chainlink `latestRoundData()` is called without checking `updatedAt` staleness, `answeredInRound >= roundId`, or `price > 0`
- Unhandled Chainlink reverts (e.g., access-controlled feeds on some L2s) cause a total DoS of all price-dependent operations
- TWAP oracles register token pairs in the wrong order, returning the inverse price
- Balancer read-only reentrancy allows a bridge pricing function to read pool balances during a mid-transaction vault callback

**Detection Heuristics**
1. Find every `latestRoundData()` call; verify staleness, round completeness, and positivity checks are all present
2. Wrap Chainlink calls in `try/catch` and confirm a fallback oracle or cached price is used on revert
3. For TWAP implementations, verify token0/token1 order matches the actual pool ordering
4. Identify any view function reading Balancer pool balances; check whether it is callable during a Balancer vault callback from the same transaction

**False Positives**
- Oracle used only for non-critical off-chain display output
- Protocol with a correctly implemented and tested secondary oracle fallback

**Notable Historical Findings**
Juicebox audits found that Chainlink oracle data could be outdated and used without staleness validation, and separately that an unhandled Chainlink revert would lock all price oracle access. Vader Protocol had two findings where the TWAP oracle registered tokens in the wrong order and where the TWAP average itself was computed incorrectly, both producing systematically wrong prices throughout the protocol. WooFi's oracle failed silently when the Chainlink price fell outside acceptable bounds, with no fallback mechanism to prevent the bridge from operating on stale prices.

**Remediation Notes**
All Chainlink calls in bridge contracts must use the full validation pattern: positive price, non-zero `updatedAt`, `answeredInRound >= roundId`, and a configurable `MAX_STALENESS` constant. The call must be wrapped in `try/catch` with a documented fallback. Staleness thresholds must be set conservatively relative to the feed's published heartbeat and tightened for feeds on chains with unreliable sequencers.

---

### Cross-Chain Message Verification and Replay (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- Cross-chain message handlers do not verify that `msg.sender` is the trusted bridge endpoint, or do not verify the original sender address on the source chain
- Signed payloads omit `block.chainid` or the contract address, making them valid on every chain where the contract is deployed
- Processed message IDs or nonces are not tracked, allowing the same proof or signature to be submitted multiple times
- Gas limits for cross-chain execution are hardcoded or underestimated; messages that exceed the limit fail permanently with no retry path
- Diamond proxy facet upgrades do not track which cuts have been applied, allowing replay of already-executed upgrades

**Detection Heuristics**
1. Verify every cross-chain message handler checks `msg.sender == trustedBridgeEndpoint` and validates the original source chain sender
2. Confirm that processed message IDs are written to storage before execution to prevent replay within the same transaction
3. Check that signed payloads include `block.chainid`, `address(this)`, and a nonce or unique message ID
4. Verify that cross-chain gas limits are configurable and that a minimum floor is enforced at call time
5. Check `diamondCut` implementations for per-cut deduplication tracking

**False Positives**
- Bridge transport layers (LayerZero, Wormhole) that natively enforce sender verification and message deduplication at the protocol level, provided the application layer correctly validates the transport-layer guarantees
- Idempotent operations where duplicate delivery has no additional state impact

**Notable Historical Findings**
Connext audits found that router signatures could be replayed on the destination domain because the signed hash omitted the destination chain ID, and that `diamondCut` allowed already-applied facet updates to be re-executed, potentially reverting security fixes. Biconomy had a cross-chain signature replay vulnerability where a valid signature issued on one chain could be submitted on any other chain where the same contract was deployed. In the Era (zkSync) audit, priority operations could be re-executed when migrating from Gateway to L1 because neither system had recorded the operation as already processed.

**Remediation Notes**
Every cross-chain message handler must follow a strict sequence: (1) verify `msg.sender` is the bridge endpoint, (2) verify the source chain identifier and sender address, (3) mark the message as processed in storage, (4) execute. Steps one through three must be atomic and must precede any state changes or external calls. Gas limits must be parameterized per message with a protocol-enforced minimum covering the worst-case destination execution cost, and a retry or refund mechanism must exist for messages that fail due to insufficient gas.

---

### External Call Injection (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- Bridge executor or router contracts forward arbitrary calldata supplied by users to arbitrary target addresses with no whitelist restriction
- Token approvals are granted to user-supplied addresses before the external call executes
- `delegatecall` is used with a target derived from user input, running untrusted code in the contract's own storage context
- Executor contracts hold residual token balances between transactions, making them profitable to drain via crafted calldata

**Detection Heuristics**
1. Find all `.call()` and `.delegatecall()` invocations; check whether the target address originates from user input or a trusted whitelist
2. Verify function selector validation: the first 4 bytes of calldata should be compared against an allowed-selector mapping before forwarding
3. Audit token approvals granted before external calls; confirm the approval target is an immutable or whitelisted address
4. Check whether executor or router contracts accumulate token balances; if so, confirm no external call path can redirect those balances

**False Positives**
- Calls to hardcoded, immutable contract addresses where the target cannot be influenced by callers
- Functions restricted to admin or trusted operator roles with no user-controlled parameters

**Notable Historical Findings**
LI.FI's `GenericBridgeFacet` accepted arbitrary bridge addresses and calldata, allowing an attacker to pass a malicious target that drained approved tokens in a single transaction. Connext's `Executor` held unclaimed tokens between bridge steps and was exploitable via crafted calldata that redirected those tokens to an attacker-controlled address before the intended recipient claimed them. Biconomy's paymaster contract allowed theft by constructing a specific relayed transaction that triggered an arbitrary external call using the contract's own existing token approvals.

**Remediation Notes**
Bridge executor contracts must maintain an explicit allowlist of callable target addresses and permissible function selectors. Token approvals must be granted only to whitelisted addresses, consumed atomically in the same transaction, and revoked immediately after use. Executor contracts must not hold persistent token balances; residual tokens after each execution should be swept to a designated recovery address.

---

### Flow Rate and Rate Limiting (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- Bridge flow rate limits apply globally across all users when any single user exceeds the per-token threshold, enabling griefing at minimal cost
- Alternative entry points (e.g., deploying a second `TokenManager` instance) bypass the primary rate limit check
- Per-transfer size caps are absent, allowing a single large transfer to exhaust the bridge's available liquidity within one transaction
- Rate limit thresholds are set in nominal token amounts and are not adjusted as token prices change, making fixed thresholds economically meaningless over time

**Detection Heuristics**
1. Check whether rate limit activation triggers a global withdrawal queue or a per-token queue
2. Identify all code paths that result in a token transfer; confirm each path is subject to the same rate limit check
3. Calculate the cost for an attacker to activate the rate limit relative to the damage inflicted on legitimate users
4. Check whether large individual transfers can bypass per-period rate limits through a single transaction

**False Positives**
- Intentional global circuit breakers activated only by governance with a documented and timelocked override path
- Rate limits where the activation threshold requires economic exposure exceeding the attacker's potential benefit

**Notable Historical Findings**
Immutable's bridge had a flow rate check that activated a global withdrawal queue on the first token that exceeded its threshold, meaning a single attacker transaction just above the limit would delay every pending withdrawal for all users across all tokens. Axelar ITS had a finding where the `TokenBalance` limit could be bypassed entirely by deploying a new `TokenManager` instance, as the limit was enforced at the manager level rather than at the bridge level. A separate Axelar finding demonstrated that ERC-777 token support in the `TokenManager` broke the flow limit logic because the re-entrant hook could trigger multiple limit evaluations within a single transfer.

**Remediation Notes**
Rate limit state must be tracked and enforced per-token; activation of a restricted mode for one token must not affect withdrawals of other tokens. Every code path that moves tokens out of the bridge must pass through the same rate limit check. Token manager deployments must be authenticated to prevent bypass via new instances. Consider expressing rate limits in USD value using a price oracle rather than in nominal token amounts to maintain consistent security properties over time.

---

### State Update Inconsistency (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- Burn or cancel operations do not clear all associated mappings (e.g., `orderOwner` persists after NFT burn), enabling the next mint of the same token ID to inherit stale ownership
- Signer count or threshold counters are decremented unconditionally rather than only when the removed entity was actually active, causing the threshold to exceed the valid signer count
- Domain separator or name hash caches are not invalidated when the underlying value changes
- Array swap-and-pop removals update the array but not the associated index mapping, corrupting future lookups on the swapped element
- Cross-chain accounting fails to synchronize source-chain locked amounts with destination-chain minted amounts when intermediate steps fail or are retried

**Detection Heuristics**
1. For every remove, burn, or cancel operation, enumerate all state variables referencing the affected entity and verify each is cleared
2. Check counter variables (signer counts, total supply, cumulative balances) for correctness on both increment and decrement paths
3. Verify that cached computed values (domain separators, price accumulators) are invalidated when any of their inputs change
4. For swap-and-pop array patterns, confirm the index mapping for the moved element is updated before the pop executes

**False Positives**
- Deliberately lazy state updates reconciled by a keeper in a subsequent transaction, with the interim inconsistency documented and bounded
- State variables used only for historical reference or off-chain indexing with no on-chain security impact

**Notable Historical Findings**
CLOBER audits found that `orderOwner` was not zeroed after an NFT burn, allowing the next mint of the same token ID to inherit stale ownership and enabling order theft. Connext audits identified that the domain separator was not rebuilt after a `name` change, causing EIP-712 signatures to silently fail for users whose clients had cached the new name. Hats Protocol had a finding where `_removeSigner` decremented `signerCount` even when the removed signer was already invalid, causing the threshold to be set higher than the actual number of valid signers and bricking the Safe module.

**Remediation Notes**
Any operation that removes an entity from the bridge (token manager deregistration, signer removal, route deletion) must include an explicit cleanup pass over all mappings that reference that entity. Threshold and counter arithmetic must guard against double-decrement by checking whether the entity is active before modifying the counter. Domain separators must be rebuilt atomically within any setter that modifies the values they encode.

---

### ERC4626 Vault Integration Issues (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- Bridge-connected vaults are vulnerable to first-depositor share price inflation when no virtual shares offset is present
- The `mint` function uses the `shares` parameter in the `transferFrom` call where it should use the computed `assets` value, under-collecting tokens
- `maxDeposit`, `maxWithdraw`, and `maxRedeem` do not return 0 when the vault is paused or at capacity, causing integrators to attempt operations that will revert
- Lossy yield strategies cause the vault exchange rate to fall below 1:1, under-collateralizing the bridge's outstanding liabilities
- Preview functions disagree with actual execution amounts due to fees or limits not reflected in the preview

**Detection Heuristics**
1. Check for virtual shares or an equivalent mechanism protecting against share price inflation on the first deposit
2. Compare `previewDeposit`/`previewRedeem` return values against actual `deposit`/`redeem` return values; any discrepancy indicates a specification violation
3. Verify that all `max*` functions return 0 when the contract is paused or capped
4. Check that `mint()` and `deposit()` use the correct parameter (`assets` vs. `shares`) in the token `transferFrom` call
5. Verify round-trip consistency: depositing then immediately redeeming must not lose funds beyond a 1-wei rounding tolerance

**False Positives**
- Vaults using OpenZeppelin's ERC4626 virtual shares offset, which is an accepted mitigation for inflation attacks
- Vaults that document and disclose non-compliance with specific EIP-4626 clauses

**Notable Historical Findings**
Tribe's `xERC4626` used the wrong `amount` parameter in the `mint` function, causing callers to receive shares without transferring the correct asset quantity. PoolTogether v5 audits produced numerous ERC4626 compliance findings, including a case where the vault's internal exchange rate could only decrease and never recover from a lossy strategy, permanently under-collateralizing outstanding shares over time. GoGoPool's `TokenggAVAX` returned incorrect values from `maxWithdraw` and `maxRedeem` when the contract was paused, causing external integrators to attempt operations that would immediately revert.

**Remediation Notes**
Bridges that custody assets in ERC4626 vaults must validate full specification compliance before integration, including paused-state behavior of all `max*` functions. First-deposit inflation attacks are mitigated by OpenZeppelin's virtual shares pattern; any custom vault implementation must replicate this protection. Exchange rate decreases due to lossy strategies must be handled explicitly, either by pausing withdrawals or by maintaining a separate solvency reserve proportional to outstanding bridge liabilities.

---

### Non-Standard Token Handling (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- Bridge accepts fee-on-transfer tokens but records the nominal transfer amount rather than the actual balance delta, overstating the locked amount and permitting over-release on the destination chain
- USDT-style tokens require the approval amount to be set to 0 before setting a new non-zero value; omitting this causes a revert that blocks bridge operations
- ERC-777 tokens trigger `tokensReceived` callbacks that re-enter bridge logic before accounting is finalized
- Tokens with non-standard or mutable `decimals()` values are not normalized before cross-chain amount encoding
- Rebasing tokens (e.g., stETH, aTokens) change their balance between the lock event and the corresponding release, causing systematic accounting drift

**Detection Heuristics**
1. Confirm all `transferFrom` calls use a balance-before/balance-after delta to record the actual received amount rather than the input parameter
2. Search for `IERC20(token).approve(` calls that do not reset allowance to 0 before setting a new value
3. Identify tokens explicitly supported by the bridge; flag any with non-standard behavior (fee, rebase, ERC-777) and verify each has explicit handling
4. Check `decimals()` usage in all cross-chain amount scaling paths; verify it is called dynamically rather than hardcoded
5. Verify `safeTransfer` and `safeTransferFrom` are used throughout rather than bare `transfer` and `transferFrom`

**False Positives**
- Bridges that explicitly document and enforce a whitelist of non-fee-on-transfer, non-rebasing tokens
- Approval calls where the contract is known to consume the full allowance in the same transaction and the token is not USDT-like

**Notable Historical Findings**
Axelar ITS had balance tracking completely broken for rebasing tokens because the bridge locked a snapshot amount but the rebased balance changed before and after the cross-chain operation, enabling attackers to exploit the gap. A separate Axelar finding showed that ERC-777 reentrancy allowed `expressReceiveToken` to be re-entered before the express delivery was marked as settled, enabling double delivery. LI.FI received multiple findings for not resetting token allowances after swaps, leaving residual approvals that could be exploited by subsequent callers interacting with the same bridge contract.

**Remediation Notes**
Bridge contracts must use the balance-delta pattern for every inbound token transfer unconditionally, regardless of whether the token is expected to be fee-on-transfer. USDT compatibility requires the two-step approve pattern (set to 0, then set to amount). ERC-777 support requires re-entrancy guards on all token receipt paths. Rebasing tokens should either be explicitly unsupported and blocked, or converted to a non-rebasing wrapper before bridging.

---

### Native ETH Handling (no fv-sol equivalent — candidate for new entry)

**Protocol-Specific Preconditions**
- `msg.value` sent to a bridge function is not forwarded to the downstream messaging layer, leaving ETH permanently stranded in the bridge contract
- Excess ETH above the required fee is not refunded to the caller
- Inconsistent ETH/WETH handling causes some code paths to wrap ETH while others pass it as native, resulting in mismatched accounting on the destination side
- Arbitrum retryable ticket creation uses an incorrect function variant, causing aliasing issues that prevent fund recovery
- Wormhole bridge facets omit the `{value: msg.value}` syntax on the bridge call, sending the message without the required attached value

**Detection Heuristics**
1. For every `payable` function, trace `msg.value` through all downstream calls and verify none is left unaccounted
2. Check whether excess ETH (`msg.value - requiredFee`) is explicitly refunded to `msg.sender` using a success-checked low-level call
3. Audit ETH-to-WETH wrapping paths for asymmetry: every `weth.deposit` should have a corresponding `weth.withdraw` on paths that need native ETH output
4. Verify L2-specific bridge calls (Optimism, Arbitrum, zkSync) use the correct function signatures for fee forwarding and refund aliasing

**False Positives**
- Contracts that intentionally collect excess ETH as a fee, with this behavior documented
- Atomic wrap/unwrap within a single transaction where no value can be stranded

**Notable Historical Findings**
LI.FI's Wormhole facet was found not to include the native token in the bridge call, and the Arbitrum facet used the wrong function to create retryable tickets, causing submitted fees to be unrecoverable. Connext's executor and asset logic handled native tokens inconsistently across code paths, causing `execute()` to revert when the bridge had forwarded native ETH instead of WETH. Decent's bridge sent any ETH refunded by the destination router to the `DecentBridgeAdapter` contract address rather than back to the original caller, permanently locking refunded value.

**Remediation Notes**
Every `payable` bridge function must forward `msg.value` in full to the underlying messaging layer using explicit `{value: msg.value}` syntax. Excess ETH must be returned to `msg.sender` via a low-level call with a checked success flag. ETH and WETH must be handled through a single canonical adapter function to eliminate mixed-handling inconsistencies. L2-specific fee mechanics (Arbitrum, Optimism, zkSync) must be tested with the exact function variants documented by the respective bridge infrastructure.
