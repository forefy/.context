# FV-SOL-3 Arithmetic Errors Quick Detection Patterns

Supplementary attack patterns for this category. Each entry captures specific detection signals and false positive conditions from real-world audit findings.

---

**32 Small-Type Arithmetic Overflow Before Upcast**

**D:** Arithmetic on `uint8`/`uint16`/`uint32` before assigning to wider type: `uint256 result = a * b` where `a`,`b` are `uint8`. Overflow happens in narrow type before widening. Solidity 0.8 overflow check is still on the narrow type.

**FP:** Operands explicitly upcast before operation: `uint256(a) * uint256(b)`. SafeCast used.

---

**45 Integer Overflow / Underflow**

**D:** Arithmetic in `unchecked {}` (>=0.8) without prior bounds check: subtraction without `require(amount <= balance)`, large multiplications. Any arithmetic in <0.8 without SafeMath.

**FP:** Range provably bounded by earlier checks in same function. `unchecked` only for `++i` loop increments where `i < arr.length`.

---

**70 Unsafe Downcast / Integer Truncation**

**D:** `uint128(largeUint256)` without bounds check. Solidity >= 0.8 silently truncates on downcast (no revert). Dangerous in price feeds, share calculations, timestamps.

**FP:** `require(x <= type(uint128).max)` before cast. OZ `SafeCast` used.

---

**85 Assembly Arithmetic Silent Overflow and Division-by-Zero**

**D:** Arithmetic inside `assembly {}` (Yul) does not revert on overflow/underflow (wraps like `unchecked`) and division by zero returns 0 instead of reverting. Developers accustomed to Solidity 0.8 checked math may not expect this.

**FP:** Manual overflow checks in assembly (`if gt(result, x) { revert(...) }`). Denominator checked before `div`. Assembly block is read-only (`mload`/`sload` only, no arithmetic).

---
