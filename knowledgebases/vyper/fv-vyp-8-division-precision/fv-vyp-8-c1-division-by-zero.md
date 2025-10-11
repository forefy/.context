# FV-VYP-8-C1 Division by Zero

## Bad

```vyper
# @version ^0.3.0

@external
@view
def calculate_share(total_amount: uint256, total_shares: uint256) -> uint256:
    # Vulnerable: division by zero
    return total_amount / total_shares

@external
@view
def calculate_percentage(value: uint256, total: uint256) -> uint256:
    # Vulnerable: no zero check
    return (value * 100) / total
```

## Good

```vyper
# @version ^0.3.0

@external
@view
def calculate_share(total_amount: uint256, total_shares: uint256) -> uint256:
    # Safe: check for zero before division
    assert total_shares > 0, "No shares available"
    return total_amount / total_shares

@external
@view
def calculate_percentage(value: uint256, total: uint256) -> uint256:
    # Safe: handle zero case explicitly
    if total == 0:
        return 0
    return (value * 100) / total
```