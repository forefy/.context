# FV-VYP-2-C1 Arithmetic Overflow

## Bad

```vyper
# @version ^0.3.0

total_supply: public(uint256)

@external
def mint(amount: uint256):
    # Vulnerable: no overflow check
    self.total_supply += amount
```

## Good

```vyper
# @version ^0.3.0

total_supply: public(uint256)
MAX_SUPPLY: constant(uint256) = 1000000 * 10**18

@external
def mint(amount: uint256):
    # Safe: check for overflow before operation
    assert self.total_supply + amount >= self.total_supply, "Overflow"
    assert self.total_supply + amount <= MAX_SUPPLY, "Max supply exceeded"
    self.total_supply += amount
```