# FV-SOL-5 Logic Errors Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**[3] Same-Block Deposit-Withdraw Exploiting Snapshot-Based Benefits**

**D:** Protocol calculates yield, rewards, voting power, or insurance coverage based on balance at a single snapshot point. No minimum lock period between deposit and withdrawal. Attacker flash-loans tokens, deposits, triggers snapshot (or waits for same-block snapshot), claims benefit, withdraws — all in one tx/block.

**FP:** `getPastVotes(block.number - 1)` or equivalent past-block snapshot. Minimum holding period enforced (`require(block.number > depositBlock)`). Reward accrual requires multi-block time passage.

---

**[5] Block Timestamp Dependence**

**D:** `block.timestamp` used for game outcomes, randomness (`block.timestamp % N`), or auction timing where ~15s manipulation changes outcome.

**FP:** Timestamp used only for hour/day-scale periods. Timestamp used only for event logging with no state effect.

---

**[8] Invariant or Cap Enforced on One Code Path But Not Another**

**D:** A constraint (pool cap, max supply, position limit, collateral ratio) is enforced during normal operation (e.g., `deposit()`) but not during settlement, reward distribution, interest accrual, or emergency paths. Constraint violated through the unguarded path.

**FP:** Invariant check applied in a shared modifier/internal function called by all relevant paths. Post-condition assertion validates invariant after every state change. Comprehensive integration tests verify invariant across all entry points.

---

**[9] msg.value Reuse in Loop / Multicall**

**D:** `msg.value` read inside a loop or `delegatecall`-based multicall. Each iteration/sub-call sees the full original value — credits `n * msg.value` for one payment.

**FP:** `msg.value` captured to local variable, decremented per iteration, total enforced. Function non-payable. Multicall uses `call` not `delegatecall`.

---

**[11] ERC1155 safeBatchTransferFrom Unchecked Array Lengths**

**D:** Custom `_safeBatchTransferFrom` iterates `ids`/`amounts` without `require(ids.length == amounts.length)`. Assembly-optimized paths may silently read uninitialized memory.

**FP:** OZ ERC1155 base used unmodified. Custom override asserts equal lengths as first statement.

---

**[16] extcodesize Zero in Constructor**

**D:** `require(msg.sender.code.length == 0)` as EOA check. Contract constructors have `extcodesize == 0` during execution, bypassing the check.

**FP:** Check is non-security-critical. Function protected by merkle proof, signed permit, or other mechanism unsatisfiable from constructor.

---

**[24] Cross-Chain Deployment Replay**

**D:** Deployment tx replayed on another chain. Same deployer nonce on both chains produces same CREATE address under different control. No EIP-155 chain ID protection. Ref: Wintermute.

**FP:** EIP-155 signatures. `CREATE2` via deterministic factory at same address on all chains. Per-chain deployer EOAs.

---

**[29] CREATE2 Address Squatting (Counterfactual Front-Running)**

**D:** CREATE2 salt not bound to `msg.sender`. Attacker precomputes address and deploys first. For AA wallets: attacker deploys wallet to user's counterfactual address with attacker as owner.

**FP:** Salt incorporates `msg.sender`: `keccak256(abi.encodePacked(msg.sender, userSalt))`. Factory restricts deployer. Different owner in constructor produces different address.

---

**[31] Immutable / Constructor Argument Misconfiguration**

**D:** Constructor sets `immutable` values (admin, fee, oracle, token) that can't change post-deploy. Multiple same-type `address` params where order can be silently swapped. No post-deploy verification.

**FP:** Deployment script reads back and asserts every configured value. Constructor validates: `require(admin != address(0))`, `require(feeBps <= 10000)`.

---

**[34] mstore8 Partial Write Leaving Dirty Bytes**

**D:** `mstore8` writes a single byte at a memory offset, but subsequent `mload` reads the full 32-byte word containing that byte. The remaining 31 bytes retain prior memory contents (potentially uninitialized or stale data). Pattern: building a byte array with `mstore8` in a loop, then hashing or returning the full memory region — dirty bytes corrupt the result.

**FP:** Full word zeroed with `mstore(ptr, 0)` before byte-level writes. `mload` result masked to extract only the written bytes. `mstore` used instead of `mstore8` with proper shifting.

---

**[37] Commit-Reveal Scheme Not Bound to msg.sender**

**D:** Commitment hash does not include `msg.sender`: `commit = keccak256(abi.encodePacked(value, salt))`. Attacker copies a victim's commitment from the chain/mempool and submits their own reveal for the same hash from a different address. Affects auctions, governance votes, randomness.

**FP:** Commitment includes sender: `keccak256(abi.encodePacked(msg.sender, value, salt))`. Reveal validates `msg.sender` matches stored committer.

---

**[54] Force-Feeding ETH via selfdestruct / Coinbase / CREATE2 Pre-Funding**

**D:** Contract uses `address(this).balance` for accounting or gates logic on exact balance (e.g., `require(balance == totalDeposits)`). `selfdestruct(target)`, coinbase rewards, or pre-computed `CREATE2` deposits force ETH in without calling `receive()`/`fallback()`, breaking invariants.

**FP:** Internal accounting only (`totalDeposited` state variable, never reads `address(this).balance`). Contract designed to accept arbitrary ETH (e.g., WETH wrapper).

---

**[57] Block Number as Timestamp Approximation**

**D:** Time computed as `(block.number - startBlock) * 13` assuming fixed block times. Variable across chains/post-Merge. Wrong interest/vesting/rewards.

**FP:** `block.timestamp` used for all time-sensitive calculations.

---

**[61] Bytecode Verification Mismatch**

**D:** Verified source doesn't match deployed bytecode behavior: different compiler settings, obfuscated constructor args, or `--via-ir` vs legacy pipeline mismatch. No reproducible build (no pinned compiler in config).

**FP:** Deterministic build with pinned compiler/optimizer in committed config. Verification in deployment script (Foundry `--verify`). Sourcify full match. Constructor args published.

---

**[62] Scratch Space Corruption Across Assembly Blocks**

**D:** Data written to scratch space (`0x00`–`0x3f`) in one assembly block is expected to persist and be read in a later assembly block, but intervening Solidity code (or compiler-generated code for `keccak256`, `abi.encode`, etc.) overwrites scratch space between the two blocks. Pattern: `mstore(0x00, key); mstore(0x20, slot)` in block A, then `keccak256(0x00, 0x40)` in block B with Solidity statements between them.

**FP:** All scratch space reads occur within the same contiguous assembly block as the writes. Developer explicitly rewrites scratch space before each use. No intervening Solidity code between blocks.

---

**[65] ERC1155 Fungible / Non-Fungible Token ID Collision**

**D:** ERC1155 represents both fungible and unique items with no enforcement: missing `require(totalSupply(id) == 0)` before NFT mint, or no cap preventing additional copies of supply-1 IDs.

**FP:** `require(totalSupply(id) + amount <= maxSupply(id))` with `maxSupply=1` for NFTs. Fungible/NFT ID ranges disjoint and enforced. Role tokens non-transferable.

---

**[72] Nonce Gap from Reverted Transactions (CREATE Address Mismatch)**

**D:** Deployment script uses `CREATE` and pre-computes addresses from deployer nonce. Reverted/extra tx advances nonce — subsequent deployments land at wrong addresses. Pre-configured references point to empty/wrong contracts.

**FP:** `CREATE2` used (nonce-independent). Script reads nonce from chain before computing. Addresses captured from deployment receipts, not pre-assumed.

---

**[73] Fee-on-Transfer Token Accounting**

**D:** Deposit records `deposits[user] += amount` then `transferFrom(..., amount)`. Fee-on-transfer tokens cause contract to receive less than recorded.

**FP:** Balance measured before/after: `uint256 before = token.balanceOf(this); transferFrom(...); received = balanceOf(this) - before;` and `received` used for accounting.

---

**[75] Merkle Tree Second Preimage Attack**

**D:** `MerkleProof.verify(proof, root, leaf)` where leaf derived from user input without double-hashing or type-prefixing. 64-byte input (two sibling hashes) passes as intermediate node.

**FP:** Leaves double-hashed or include type prefix. Input length enforced != 64 bytes. OZ MerkleProof >= v4.9.2 with sorted-pair variant.

---

**[76] Dirty Higher-Order Bits on Sub-256-Bit Types**

**D:** Assembly loads a value as a full 32-byte word (`calldataload`, `sload`, `mload`) but treats it as a smaller type (`address`, `uint128`, `uint8`, `bool`) without masking upper bits. Dirty bits cause incorrect comparisons, mapping key mismatches, or storage corruption. Pattern: `let addr := calldataload(4)` used directly without `and(addr, 0xffffffffffffffffffffffffffffffffffffffff)`.

**FP:** Explicit bitmask applied: `and(value, mask)` immediately after load. Value produced by a prior Solidity expression that already cleaned it. `shr(96, calldataload(offset))` pattern that naturally zeros upper bits for addresses.

---

**[78] Returndatasize-as-Zero Assumption**

**D:** Assembly uses `returndatasize()` as a gas-cheap substitute for `push 0` (saves 1 gas). If a prior `call`/`staticcall` in the same execution context returned data, `returndatasize()` is nonzero, corrupting the intended zero value. Pattern: `let ptr := returndatasize()` or `mstore(returndatasize(), value)` after an external call has been made.

**FP:** `returndatasize()` used as zero only at the very start of execution before any external calls. Used immediately after a controlled call where the return size is known. Used as an actual size measurement (its intended purpose).

---

**[84] Rebasing / Elastic Supply Token Accounting**

**D:** Contract holds rebasing tokens (stETH, AMPL, aTokens) and caches `balanceOf(this)`. After rebase, cached value diverges from actual balance.

**FP:** Rebasing tokens blocked at code level (revert/whitelist). Accounting reads `balanceOf` live. Wrapper tokens (wstETH) used.

---

**[88] Missing Chain ID Validation in Deployment Configuration**

**D:** Deploy script reads `$RPC_URL` from `.env` without `eth_chainId` assertion. Foundry script without `--chain-id` flag or `block.chainid` check. No dry-run before broadcast.

**FP:** `require(block.chainid == expectedChainId)` at script start. CI validates chain ID before deployment.

---

**[89] Array `delete` Leaves Zero-Value Gap Instead of Removing Element**

**D:** `delete array[index]` resets element to zero but does not shrink the array or shift subsequent elements. Iteration logic treats the zeroed slot as a valid entry — phantom zero-address recipients, skipped distributions, or inflated `length`.

**FP:** Swap-and-pop pattern used (`array[index] = array[length - 1]; array.pop()`). Iteration skips zero entries explicitly. EnumerableSet or similar library used.

---

**[96] Deployment Transaction Front-Running (Ownership Hijack)**

**D:** Deployment tx sent to public mempool without private relay. Attacker extracts bytecode and deploys first (or front-runs initialization). Pattern: `eth_sendRawTransaction` via public RPC, constructor sets `owner = msg.sender`.

**FP:** Private relay used (Flashbots Protect, MEV Blocker). Owner passed as constructor arg, not `msg.sender`. Chain without public mempool. CREATE2 salt tied to deployer.

---

**[97] Duplicate Items in User-Supplied Array**

**D:** Function accepts array parameter (e.g., `claimRewards(uint256[] calldata tokenIds)`) without checking for duplicates. User passes same ID multiple times, claiming rewards/voting/withdrawing repeatedly in one call.

**FP:** Duplicate check via mapping (`require(!seen[id]); seen[id] = true`). Sorted-unique input enforced (`require(ids[i] > ids[i-1])`). State zeroed on first claim (second iteration reverts naturally).

---

**[99] Calldataload / Calldatacopy Out-of-Bounds Read**

**D:** `calldataload(offset)` where `offset` is user-controlled or exceeds actual calldata length. Reading past `calldatasize()` returns zero-padded bytes silently (no revert), producing phantom zero values that pass downstream logic as valid inputs. Pattern: `calldataload(add(4, mul(index, 32)))` without `require(index < paramCount)`.

**FP:** `calldatasize()` validated before assembly block (e.g., Solidity ABI decoder already checked). Static offsets into known fixed-length function signatures. Explicit `if lt(calldatasize(), minExpected) { revert(0,0) }` guard.

---

**[102] Non-Atomic Multi-Contract Deployment (Partial System Bootstrap)**

**D:** Deployment script deploys interdependent contracts across separate transactions. Midway failure leaves half-deployed state with missing references or unwired contracts. Pattern: multiple `vm.broadcast()` blocks or sequential `await deploy()` with no idempotency checks.

**FP:** Single `vm.startBroadcast()`/`vm.stopBroadcast()` block. Factory deploys+wires all in one tx. Script is idempotent. Hardhat-deploy with resumable migrations.

---

**[109] ERC721 Approval Not Cleared in Custom Transfer Override**

**D:** Custom `transferFrom` override skips `super._transfer()` or `super.transferFrom()`, missing the `delete _tokenApprovals[tokenId]` step. Previous approval persists under new owner.

**FP:** Override calls `super.transferFrom` or `super._transfer` internally. Or explicitly deletes approval / calls `_approve(address(0), tokenId, owner)`.

---

**[111] Weak On-Chain Randomness**

**D:** Randomness from `block.prevrandao`, `blockhash(block.number - 1)`, `block.timestamp`, `block.coinbase`, or combinations. Validator-influenceable or visible before inclusion.

**FP:** Chainlink VRF v2+. Commit-reveal with future-block reveal and slashing for non-reveal.

---

**[115] Nested Mapping Inside Struct Not Cleared on `delete`**

**D:** `delete myMapping[key]` on struct containing `mapping` or dynamic array. `delete` zeroes primitives but not nested mappings. Reused key exposes stale values.

**FP:** Nested mapping manually cleared before `delete`. Key never reused after deletion.

---

**[127] Missing chainId (Cross-Chain Replay)**

**D:** Signed payload omits `chainId`. Valid signature replayable on forks/other EVM chains. Or `chainId` hardcoded at deployment instead of `block.chainid`.

**FP:** EIP-712 domain separator includes dynamic `chainId: block.chainid` and `verifyingContract`.

---

**[132] Hardcoded Network-Specific Addresses**

**D:** Literal `address(0x...)` constants for external dependencies (oracles, routers, tokens) in deployment scripts/constructors. Wrong contracts on different chains.

**FP:** Per-chain config file keyed by chain ID. Script asserts `block.chainid`. Addresses passed as constructor args from environment. Deterministic cross-chain addresses (e.g., Permit2).

---

**[138] Merkle Proof Reuse — Leaf Not Bound to Caller**

**D:** Merkle leaf doesn't include `msg.sender`: `MerkleProof.verify(proof, root, keccak256(abi.encodePacked(amount)))`. Proof can be front-run from different address.

**FP:** Leaf encodes `msg.sender`: `keccak256(abi.encodePacked(msg.sender, amount))`. Proof recorded as consumed after first use.

---

**[146] Insufficient Gas Forwarding / 63/64 Rule**

**D:** External call without minimum gas budget: `target.call(data)` with no gas check. 63/64 rule leaves subcall with insufficient gas. In relayer patterns, subcall silently fails but outer tx marks request as "processed."

**FP:** `require(gasleft() >= minGas)` before subcall. Return value + returndata both checked. EIP-2771 with verified gas parameter.

---

**[152] Stale Cached ERC20 Balance from Direct Token Transfers**

**D:** Contract tracks holdings in state variable (`totalDeposited`, `_reserves`) updated only through protocol functions. Direct `token.transfer(contract)` inflates real balance beyond cached value. Attacker exploits gap for share pricing/collateral manipulation.

**FP:** Accounting reads `balanceOf(this)` live. Cached value reconciled at start of every state-changing function. Direct transfers treated as revenue.

---

**[157] abi.encodePacked Hash Collision with Dynamic Types**

**D:** `keccak256(abi.encodePacked(a, b))` where two+ args are dynamic types (`string`, `bytes`, dynamic arrays). No length prefix means different inputs produce identical hashes. Affects permits, access control keys, nullifiers.

**FP:** `abi.encode()` used instead. Only one dynamic type arg. All args fixed-size.

---

**[166] Free Memory Pointer Corruption**

**D:** Assembly block writes to memory at fixed offsets (e.g., `mstore(0x80, val)`) without reading or updating the free memory pointer at `0x40`. Subsequent Solidity code allocates memory from stale pointer, overwriting the assembly-written data — or vice versa. Second pattern: assembly sets `mstore(0x40, newPtr)` to an incorrect value, causing later Solidity allocations to overlap prior data.

**FP:** Assembly block reads `mload(0x40)`, writes only above that offset, then updates `mstore(0x40, newFreePtr)`. Or block only uses scratch space (`0x00`–`0x3f`). Block annotated `memory-safe` and verified to comply. Ref: Solidity optimizer bug in 0.8.13–0.8.14 mishandled cross-block memory writes.

---

**[169] Hardcoded Calldataload Offset Bypass via Non-Canonical ABI Encoding**

**D:** Assembly reads a field at hardcoded calldata offset (`calldataload(164)`) assuming standard ABI layout. Attacker crafts non-canonical encoding — manipulated dynamic-type offset pointers or padding — so a different value sits at the expected position.

**FP:** Field decoded via `abi.decode()` (compiler bounds-checked). No hardcoded `calldataload` offsets — parameters extracted through Solidity's typed calldata accessors. `calldatasize() >= expected` validated before reading.

---

**[170] Calldata Input Malleability**

**D:** Contract hashes raw calldata for uniqueness (`processedHashes[keccak256(msg.data)]`). Dynamic-type ABI encoding uses offset pointers — multiple distinct calldata layouts decode to identical values. Attacker bypasses dedup with semantically equivalent but bytewise-different calldata.

**FP:** Uniqueness check hashes decoded parameters: `keccak256(abi.encode(decodedParams))`. Nonce-based replay protection. Only fixed-size types in signature (no encoding ambiguity).
