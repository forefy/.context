# FV-SOL-4 Bad Access Control Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**1 Signature Malleability**

**D:** Raw `ecrecover` without `s <= 0x7FFF...20A0` validation. Both `(v,r,s)` and `(v',r,s')` recover same address. Bypasses signature-based dedup.

**FP:** OZ `ECDSA.recover()` used (validates `s` range). Message hash used as dedup key, not signature bytes.

---

**15 Missing or Incorrect Access Modifier**

**D:** State-changing function (`setOwner`, `withdrawFunds`, `mint`, `pause`, `setOracle`) has no access guard or modifier references uninitialized variable. `public`/`external` on privileged operations with no restriction.

**FP:** Function is intentionally permissionless with non-critical worst-case outcome (e.g., advancing a public time-locked process).

---

**23 Improper Flash Loan Callback Validation**

**D:** `onFlashLoan` callback doesn't verify `msg.sender == lendingPool`, or doesn't check `initiator`/`token`/`amount`. Callable directly without real flash loan.

**FP:** Both `msg.sender == address(lendingPool)` and `initiator == address(this)` validated. Token/amount checked.

---

**27 ecrecover Returns address(0) on Invalid Signature**

**D:** Raw `ecrecover` without `require(recovered != address(0))`. If `authorizedSigner` is uninitialized or `permissions[address(0)]` is non-zero, garbage signature gains privileges.

**FP:** OZ `ECDSA.recover()` used (reverts on address(0)). Explicit zero-address check present.

---

**33 ERC4626 Missing Allowance Check in withdraw() / redeem()**

**D:** `withdraw(assets, receiver, owner)` / `redeem(shares, receiver, owner)` where `msg.sender != owner` but no allowance check/decrement before burning shares. Any address can burn arbitrary owner's shares.

**FP:** `_spendAllowance(owner, caller, shares)` called unconditionally when `caller != owner`. OZ ERC4626 without custom overrides.

---

**49 ERC721 onERC721Received Arbitrary Caller Spoofing**

**D:** `onERC721Received` uses parameters (`from`, `tokenId`) to update state without verifying `msg.sender` is the expected NFT contract. Anyone calls directly with fabricated parameters.

**FP:** `require(msg.sender == address(nft))` before state update. Function is view-only or reverts unconditionally.

---

**51 Missing Nonce (Signature Replay)**

**D:** Signed message has no per-user nonce, or nonce present but never stored/incremented after use. Same signature resubmittable.

**FP:** Monotonic per-signer nonce in signed payload, checked and incremented atomically. Or `usedSignatures[hash]` mapping.

---

**63 ERC1155 Custom Burn Without Caller Authorization**

**D:** Public `burn(address from, uint256 id, uint256 amount)` callable by anyone without verifying `msg.sender == from` or operator approval. Any caller burns another user's tokens.

**FP:** `require(from == msg.sender || isApprovedForAll(from, msg.sender))` before `_burn`. OZ `ERC1155Burnable` used.

---

**79 tx.origin Authentication**

**D:** `require(tx.origin == owner)` used for auth. Phishable via intermediary contract.

**FP:** `tx.origin == msg.sender` used only as anti-contract check, not auth.

---

**91 Write to Arbitrary Storage Location**

**D:** (1) `sstore(slot, value)` where `slot` derived from user input without bounds. (2) Solidity <0.6: direct `arr.length` assignment + indexed write at crafted large index wraps slot arithmetic.

**FP:** Assembly is read-only (`sload` only). Slot is compile-time constant or non-user-controlled. Solidity >= 0.6 used.

---

**101 Deployer Privilege Retention Post-Deployment**

**D:** Deployer EOA retains owner/admin/minter/pauser/upgrader after deployment script completes. Pattern: `Ownable` sets `owner = msg.sender` with no `transferOwnership()`. `AccessControl` grants `DEFAULT_ADMIN_ROLE` to deployer with no `renounceRole()`.

**FP:** Script includes `transferOwnership(multisig)`. Admin role granted to timelock/governance, deployer renounces. `Ownable2Step` with pending owner set to multisig.

---

**121 Arbitrary External Call with User-Supplied Target and Calldata**

**D:** `target.call{value: v}(data)` where `target` or `data` (or both) are caller-supplied parameters. Attacker crafts calldata to invoke unintended functions on the target (e.g., `transferFrom` on an approved ERC20, or `safeTransferFrom` on held NFTs), stealing assets the contract holds or has approvals for.

**FP:** Target restricted to hardcoded/whitelisted address. Calldata function selector restricted to known-safe set. No token approvals or asset holdings on the calling contract. `delegatecall` vector covered separately (V58/V105); this covers `call`.

---

**134 ERC1155 ID-Based Role Access Control With Publicly Mintable Role Tokens**

**D:** Access control via `require(balanceOf(msg.sender, ROLE_ID) > 0)` where `mint` for those IDs is not separately gated. Role tokens transferable by default.

**FP:** Minting role-token IDs gated behind separate access control. Role tokens non-transferable (`_beforeTokenTransfer` reverts for non-mint/burn). Dedicated non-token ACL used.

---

**148 ERC1155 setApprovalForAll Grants All-Token-All-ID Access**

**D:** Protocol requires `setApprovalForAll(protocol, true)` for deposits/staking. No per-ID or per-amount granularity -- operator can transfer any ID at full balance.

**FP:** Protocol uses direct `safeTransferFrom` with user as `msg.sender`. Operator is immutable contract with escrow-only transfer logic.

---

**161 ERC-1271 isValidSignature Delegated to Untrusted Module**

**D:** `isValidSignature(hash, sig)` delegated to externally-supplied contract without whitelist check. Malicious module always returns `0x1626ba7e`, passing all signature checks.

**FP:** Delegation only to owner-controlled whitelist. Module registry has timelock/guardian approval.

---
