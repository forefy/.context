# FV-VYP-8-C2 Precision Loss in Division

## Bad

```vyper
# @version ^0.3.0

@external
@view
def calculate_fee(amount: uint256, fee_rate: uint256) -> uint256:
    # Vulnerable: precision loss with small amounts
    return (amount * fee_rate) / 10000  # fee_rate in basis points

@external
@view
def split_payment(total: uint256, participants: uint256) -> uint256:
    # Vulnerable: remainder is lost
    return total / participants
```

## Good

```vyper
# @version ^0.3.0

PRECISION: constant(uint256) = 10**18

@external
@view
def calculate_fee(amount: uint256, fee_rate: uint256) -> uint256:
    # Safe: use higher precision for calculations
    fee_with_precision: uint256 = (amount * fee_rate * PRECISION) / 10000
    return fee_with_precision / PRECISION

@external
@view
def split_payment(total: uint256, participants: uint256) -> (uint256, uint256):
    # Safe: return both quotient and remainder
    per_participant: uint256 = total / participants
    remainder: uint256 = total % participants
    return per_participant, remainder
```