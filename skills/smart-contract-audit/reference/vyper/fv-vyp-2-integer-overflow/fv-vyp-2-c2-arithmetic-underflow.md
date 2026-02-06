# FV-VYP-2-C2 Arithmetic Underflow

## Bad

```vyper
# @version ^0.3.0

balances: public(HashMap[address, uint256])

@external
def transfer(to: address, amount: uint256):
    # Vulnerable: no underflow check
    self.balances[msg.sender] -= amount
    self.balances[to] += amount
```

## Good

```vyper
# @version ^0.3.0

balances: public(HashMap[address, uint256])

@external
def transfer(to: address, amount: uint256):
    # Safe: check for sufficient balance before subtraction
    assert self.balances[msg.sender] >= amount, "Insufficient balance"
    self.balances[msg.sender] -= amount
    self.balances[to] += amount
```