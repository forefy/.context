# FV-SOL-7 Proxy Insecurities Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**[6] Beacon Proxy Single-Point-of-Failure Upgrade**

**D:** Multiple proxies read implementation from single Beacon. Compromising Beacon owner upgrades all proxies at once. `UpgradeableBeacon.owner()` returns single EOA.

**FP:** Beacon owner is multisig + timelock. `Upgraded` events monitored. Per-proxy upgrade authority where isolation required.

---

**[18] Re-initialization Attack**

**D:** V2 uses `initializer` instead of `reinitializer(2)`. Or upgrade resets initialized counter / storage-collides bool to false. Ref: AllianceBlock (2024).

**FP:** `reinitializer(version)` with correctly incrementing versions for V2+. Tests verify `initialize()` reverts after first call.

---

**[20] Immutable Variable Context Mismatch**

**D:** Implementation uses `immutable` variables (embedded in bytecode, not storage). Proxy `delegatecall` gets implementation's hardcoded values regardless of per-proxy needs. E.g., `immutable WETH` — every proxy gets same address.

**FP:** Immutable values intentionally identical across all proxies. Per-proxy config uses storage via `initialize()`.

---

**[28] Function Selector Clash in Proxy**

**D:** Proxy and implementation share a 4-byte selector collision. Call intended for implementation routes to proxy's function (or vice versa).

**FP:** Transparent proxy pattern (admin/user call routing separates namespaces). UUPS with no custom proxy functions — all calls delegate unconditionally.

---

**[36] Arbitrary `delegatecall` in Implementation**

**D:** Implementation exposes `delegatecall` to user-supplied address without restriction. Pattern: `target.delegatecall(data)` where `target` is caller-controlled. Ref: Furucombo (2021).

**FP:** Target is hardcoded immutable address. Whitelist of approved targets enforced. `call` used instead.

---

**[46] Function Selector Clashing (Proxy Backdoor)**

**D:** Proxy contains a function whose 4-byte selector collides with an implementation function. User calls route to proxy logic instead of delegating.

**FP:** Transparent proxy pattern separates admin/user routing. UUPS proxy has no custom functions — all calls delegate.

---

**[48] UUPS Upgrade Logic Removed in New Implementation**

**D:** New UUPS implementation doesn't inherit `UUPSUpgradeable` or removes `upgradeTo`/`upgradeToAndCall`. Proxy permanently loses upgrade capability. Pattern: V2 missing `_authorizeUpgrade` override.

**FP:** Every version inherits `UUPSUpgradeable`. Tests verify `upgradeTo` works after each upgrade. OZ upgrades plugin checks in CI.

---

**[53] Diamond Proxy Cross-Facet Storage Collision**

**D:** EIP-2535 Diamond facets declare storage variables without EIP-7201 namespaced storage. Multiple facets independently start at slot 0, writing to same slots.

**FP:** All facets use single `DiamondStorage` struct at namespaced position (EIP-7201). No top-level state variables in facets.

---

**[58] Transparent Proxy Admin Routing Confusion**

**D:** Admin address also used for regular protocol interactions. Calls from admin route to proxy admin functions instead of delegating — silently failing or executing unintended logic.

**FP:** Dedicated `ProxyAdmin` contract used exclusively for admin calls. OZ `TransparentUpgradeableProxy` enforces separate admin.

---

**[74] Assembly Delegatecall Missing Return/Revert Propagation**

**D:** Proxy fallback written in assembly performs `delegatecall` but omits one or more required steps: (1) not copying full calldata via `calldatacopy`, (2) not copying return data via `returndatacopy(0, 0, returndatasize())`, (3) not branching on the result to `return(0, returndatasize())` on success or `revert(0, returndatasize())` on failure. Silent failures or swallowed reverts.

**FP:** Complete proxy pattern: `calldatacopy(0, 0, calldatasize())` → `delegatecall(gas(), impl, 0, calldatasize(), 0, 0)` → `returndatacopy(0, 0, returndatasize())` → `switch result case 0 { revert(0, returndatasize()) } default { return(0, returndatasize()) }`. OZ Proxy.sol used.

---

**[94] Upgrade Race Condition / Front-Running**

**D:** `upgradeTo(V2)` and post-upgrade config calls are separate txs in public mempool. Window for front-running (exploit old impl) or sandwiching between upgrade and config.

**FP:** `upgradeToAndCall()` bundles upgrade + init. Private mempool (Flashbots Protect). V2 safe with V1 state from block 0. Timelock makes execution predictable.

---

**[106] Non-Atomic Proxy Initialization (Front-Running `initialize()`)**

**D:** Proxy deployed in one tx, `initialize()` called in separate tx. Uninitialized proxy front-runnable. Pattern: `new TransparentUpgradeableProxy(impl, admin, "")` with empty data, separate `initialize()`. Ref: Wormhole (2022).

**FP:** Proxy constructor receives init calldata atomically: `new TransparentUpgradeableProxy(impl, admin, abi.encodeCall(...))`. OZ `deployProxy()` used.

---

**[112] Delegatecall to Untrusted Callee**

**D:** `address(target).delegatecall(data)` where `target` is user-provided or unconstrained.

**FP:** `target` is hardcoded immutable verified library address.

---

**[113] UUPS `_authorizeUpgrade` Missing Access Control**

**D:** `function _authorizeUpgrade(address) internal override {}` with empty body and no access modifier. Anyone can call `upgradeTo()`. Ref: CVE-2021-41264.

**FP:** `_authorizeUpgrade()` has `onlyOwner` or equivalent. Multisig/governance controls owner role.

---

**[118] Proxy Admin Key Compromise**

**D:** `ProxyAdmin.owner()` returns EOA, not multisig/governance; no timelock on `upgradeTo`. Ref: PAID Network (2021), Ankr (2022).

**FP:** Multisig (threshold >= 2) + timelock (24-72h). Admin role separate from operational roles.

---

**[123] Minimal Proxy (EIP-1167) Implementation Destruction**

**D:** EIP-1167 clones `delegatecall` a fixed implementation. If implementation is destroyed, all clones become no-ops with locked funds. Pattern: `Clones.clone(impl)` where impl has no `selfdestruct` protection or is uninitialized.

**FP:** No `selfdestruct` in implementation. `_disableInitializers()` in constructor. Post-Dencun: code not destroyed. Beacon proxies used for upgradeability.

---

**[130] Diamond Proxy Facet Selector Collision**

**D:** EIP-2535 Diamond where two facets register same 4-byte selector. Malicious facet via `diamondCut` hijacks calls to critical functions. Pattern: `diamondCut` adds facet with overlapping selectors, no on-chain collision check.

**FP:** `diamondCut` validates no selector collisions. `DiamondLoupeFacet` enumerates/verifies selectors post-cut. Multisig + timelock on `diamondCut`.

---

**[139] Uninitialized Implementation Takeover**

**D:** Implementation behind proxy has `initialize()` but constructor lacks `_disableInitializers()`. Attacker calls `initialize()` on implementation directly, becomes owner, can upgrade to malicious contract. Ref: Wormhole (2022), Parity (2017).

**FP:** Constructor contains `_disableInitializers()`. OZ `Initializable` correctly gates the function. Not behind a proxy (standalone).

---

**[149] Storage Layout Collision Between Proxy and Implementation**

**D:** Proxy declares state variables at sequential slots (not EIP-1967). Implementation also starts at slot 0. Proxy's admin overlaps implementation's `initialized` flag. Ref: Audius (2022).

**FP:** EIP-1967 slots. OZ Transparent/UUPS pattern. No state variables in proxy contract.

---

**[151] Diamond Shared-Storage Cross-Facet Corruption**

**D:** EIP-2535 Diamond facets declare top-level state variables (plain `uint256 foo`) instead of namespaced storage structs. Multiple facets independently start at slot 0, corrupting each other.

**FP:** All facets use single `DiamondStorage` struct at namespaced position (EIP-7201). No top-level state variables. OZ `@custom:storage-location` pattern.

---

**[155] Non-Atomic Proxy Deployment Enabling CPIMP Takeover**

**D:** Same non-atomic deploy+init pattern as V76, but attacker inserts malicious middleman implementation (CPIMP) that persists across upgrades by restoring itself in ERC-1967 slot.

**FP:** Atomic init calldata in constructor. `_disableInitializers()` in implementation constructor.

---

**[162] Proxy Storage Slot Collision**

**D:** Proxy stores `implementation`/`admin` at sequential slots (0, 1); implementation also declares variables from slot 0. Implementation writes overwrite proxy pointers.

**FP:** EIP-1967 randomized slots used. OZ Transparent/UUPS pattern.

---

**[165] Metamorphic Contract via CREATE2 + SELFDESTRUCT**

**D:** `CREATE2` deployment where deployer can `selfdestruct` and redeploy different bytecode at same address. Governance-approved code swapped before execution. Ref: Tornado Cash Governance (2023). Post-Dencun (EIP-6780): largely mitigated except same-tx create-destroy-recreate.

**FP:** Post-Dencun: `selfdestruct` no longer destroys code unless same tx as creation. `EXTCODEHASH` verified at execution time. Not deployed via `CREATE2` from mutable deployer.

---

**[168] Storage Layout Shift on Upgrade**

**D:** V2 inserts new state variable in middle of contract instead of appending. Subsequent variables shift slots, corrupting state. Also: changing variable type between versions shifts slot boundaries.

**FP:** New variables only appended. OZ storage layout validation in CI. Variable types unchanged between versions.

---
