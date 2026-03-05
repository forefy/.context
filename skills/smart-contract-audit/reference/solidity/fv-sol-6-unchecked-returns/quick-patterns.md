# FV-SOL-6 Unchecked Returns Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**10 Zero-Amount Transfer Revert**

**D:** `token.transfer(to, amount)` where `amount` can be zero (rounded fee, unclaimed yield). Some tokens (LEND, early BNB) revert on zero-amount transfers, DoS-ing distribution loops.

**FP:** `if (amount > 0)` guard before all transfers. Minimum claim amount enforced. Token whitelist verified to accept zero transfers.

---

**17 Solmate SafeTransferLib Missing Contract Existence Check**

**D:** Protocol uses Solmate's `SafeTransferLib` for ERC20 transfers. Unlike OZ `SafeERC20`, Solmate does not verify target address contains code — `transfer`/`transferFrom` to an EOA or not-yet-deployed `CREATE2` address returns success silently, crediting a phantom deposit.

**FP:** OZ `SafeERC20` used instead. Manual `require(token.code.length > 0)` check. Token addresses verified at construction/initialization.

---

**30 Return Bomb (Returndata Copy DoS)**

**D:** `(bool success, bytes memory data) = target.call(payload)` where `target` is user-supplied. Malicious target returns huge returndata; copying costs enormous gas.

**FP:** Returndata not copied (assembly call without copy, or gas-limited). Callee is hardcoded trusted contract.

---

**40 ERC1155 onERC1155Received Return Value Not Validated**

**D:** Custom ERC1155 calls `onERC1155Received` but doesn't check returned `bytes4` equals `0xf23a6e61`. Non-compliant recipient silently accepts tokens it can't handle.

**FP:** OZ ERC1155 base validates selector. Custom impl explicitly checks return value.

---

**64 ERC721 Unsafe Transfer to Non-Receiver**

**D:** `_transfer()`/`_mint()` used instead of `_safeTransfer()`/`_safeMint()`, sending NFTs to contracts without `IERC721Receiver`. Tokens permanently locked.

**FP:** All paths use `safeTransferFrom`/`_safeMint`. Function is `nonReentrant`.

---

**80 ERC20 Non-Compliant: Return Values / Events**

**D:** Custom `transfer()`/`transferFrom()` doesn't return `bool` or always returns `true` on failure. `mint()`/`burn()` missing `Transfer` events. `approve()` missing `Approval` event.

**FP:** OZ `ERC20.sol` base with no custom overrides of transfer/approve/event logic.

---

**87 Non-Standard Approve Behavior (Zero-First / Max-Approval Revert)**

**D:** (a) USDT-style: `approve()` reverts when changing from non-zero to non-zero allowance, requiring `approve(0)` first. (b) Some tokens (UNI, COMP) revert on `approve(type(uint256).max)`. Protocol calls `token.approve(spender, amount)` directly without these accommodations.

**FP:** OZ `SafeERC20.forceApprove()` or `safeIncreaseAllowance()` used. Allowance always set from zero (fresh per-tx approval). Token whitelist excludes non-standard tokens.

---

**92 Insufficient Return Data Length Validation**

**D:** Assembly `staticcall`/`call` writes return data into a fixed-size buffer (e.g., `staticcall(gas(), token, ptr, 4, ptr, 32)`) then reads `mload(ptr)` without checking `returndatasize() >= 32`. If the target is an EOA (no code, zero return data) or a non-compliant contract returning fewer bytes, `mload` reads stale memory at `ptr`, which may decode as a truthy value — silently treating a failed/absent call as success.

**FP:** `if lt(returndatasize(), 32) { revert(0,0) }` checked before reading return data. `extcodesize(target)` verified > 0 before call. Safe ERC20 pattern that handles both zero-length and 32-byte returns. Ref: Consensys Diligence — 0x Exchange bug (real exploit from missing return data length check).

---

**103 CREATE / CREATE2 Deployment Failure Silently Returns Zero**

**D:** Assembly `create(v, offset, size)` or `create2(v, offset, size, salt)` returns `address(0)` on failure (insufficient balance, collision, init code revert) but the code does not check for zero. The zero address is stored or used, and subsequent calls to `address(0)` silently succeed as no-ops (no code) or interact with precompiles.

**FP:** Immediate check: `if iszero(addr) { revert(0, 0) }` after create/create2. Address validated downstream before any state-dependent operation.

---

**128 Non-Standard ERC20 Return Values (USDT-style)**

**D:** `require(token.transfer(to, amount))` reverts on tokens returning nothing (USDT, BNB). Or return value ignored (silent failure).

**FP:** OZ `SafeERC20.safeTransfer()`/`safeTransferFrom()` used throughout.

---
