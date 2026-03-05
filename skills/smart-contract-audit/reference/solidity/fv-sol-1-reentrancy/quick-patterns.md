# FV-SOL-1 Reentrancy Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**12 ERC721/ERC1155 Callback Reentrancy**

**D:** `safeTransferFrom`/`safeMint` called before state updates. Callbacks (`onERC721Received`/`onERC1155Received`) enable reentry.

**FP:** All state committed before safe transfer. `nonReentrant` applied.

---

**50 ERC1155 totalSupply Inflation via Reentrancy Before Supply Update**

**D:** `totalSupply[id]` incremented AFTER `_mint` callback. During `onERC1155Received`, `totalSupply` is stale-low, inflating caller's share in any supply-dependent formula. Ref: OZ GHSA-9c22-pwxw-p6hx (2021).

**FP:** OZ >= 4.3.2 (patched ordering). `nonReentrant` on all mint functions. No supply-dependent logic callable from mint callback.

---

**52 Single-Function Reentrancy**

**D:** External call (`call{value:}`, `safeTransfer`, etc.) before state update — check-external-effect instead of check-effect-external (CEI).

**FP:** State updated before call (CEI followed). `nonReentrant` modifier. Callee is hardcoded immutable with known-safe receive/fallback.

---

**60 Read-Only Reentrancy**

**D:** Protocol calls `view` function (`get_virtual_price()`, `totalAssets()`) on external contract from within a callback. External contract has no reentrancy guard on view functions — returns transitional/manipulated value mid-execution.

**FP:** External view functions are `nonReentrant`. Chainlink oracle used instead. External contract's reentrancy lock checked before calling view.

---

**68 ERC1155 Batch Transfer Partial-State Callback Window**

**D:** Custom batch mint/transfer updates `_balances` and calls `onERC1155Received` per ID in loop, instead of committing all updates first then calling `onERC1155BatchReceived` once. Callback reads stale balances for uncredited IDs.

**FP:** All balance updates committed before any callback (OZ pattern). `nonReentrant` on all transfer/mint entry points.

---

**83 ERC777 tokensToSend / tokensReceived Reentrancy**

**D:** Token `transfer()`/`transferFrom()` called before state updates on a token that may implement ERC777 (ERC1820 registry). ERC777 hooks fire on ERC20-style calls, enabling reentry from sender's `tokensToSend` or recipient's `tokensReceived`.

**FP:** CEI — all state committed before transfer. `nonReentrant` on all entry points. Token whitelist excludes ERC777.

---

**98 Transient Storage Low-Gas Reentrancy (EIP-1153)**

**D:** Contract uses `transfer()`/`send()` (2300-gas) as reentrancy guard + uses `TSTORE`/`TLOAD`. Post-Cancun, `TSTORE` succeeds under 2300 gas unlike `SSTORE`. Second pattern: transient reentrancy lock not cleared at call end — persists for entire tx, causing DoS via multicall/flash loan callback.

**FP:** `nonReentrant` backed by regular storage slot (or transient mutex properly cleared). CEI followed unconditionally.

---

**105 Cross-Contract Reentrancy**

**D:** Two contracts share logical state (balances in A, collateral check in B). A makes external call before syncing state B reads. A's `ReentrancyGuard` doesn't protect B.

**FP:** State B reads is synchronized before A's external call. No re-entry path from A's callee into B.

---
