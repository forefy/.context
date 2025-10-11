# FV-VYP-1-C1 Classic Reentrancy

## Bad

```vyper
# @version ^0.3.0

balances: public(HashMap[address, uint256])

@external
def withdraw():
    balance: uint256 = self.balances[msg.sender]
    assert balance > 0, "Insufficient balance"
    
    # Vulnerable: external call before state update
    raw_call(msg.sender, b"", value=balance)
    self.balances[msg.sender] = 0
```

## Good

```vyper
# @version ^0.3.0

balances: public(HashMap[address, uint256])

@external
def withdraw():
    balance: uint256 = self.balances[msg.sender]
    assert balance > 0, "Insufficient balance"
    
    # Safe: update state before external call
    self.balances[msg.sender] = 0
    raw_call(msg.sender, b"", value=balance)
```