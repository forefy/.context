# FV-VYP-1-C2 Cross-Function Reentrancy

## Bad

```vyper
# @version ^0.3.0

balances: public(HashMap[address, uint256])

@external
def transfer(to: address, amount: uint256):
    assert self.balances[msg.sender] >= amount, "Insufficient balance"
    self.balances[msg.sender] -= amount
    self.balances[to] += amount

@external
def withdraw():
    balance: uint256 = self.balances[msg.sender]
    assert balance > 0, "No balance"
    
    # Vulnerable: external call while balance still set
    raw_call(msg.sender, b"", value=balance)
    self.balances[msg.sender] = 0
```

## Good

```vyper
# @version ^0.3.0

balances: public(HashMap[address, uint256])
locked: HashMap[address, bool]

@external
def transfer(to: address, amount: uint256):
    assert not self.locked[msg.sender], "Account locked"
    assert self.balances[msg.sender] >= amount, "Insufficient balance"
    self.balances[msg.sender] -= amount
    self.balances[to] += amount

@external
def withdraw():
    assert not self.locked[msg.sender], "Already withdrawing"
    balance: uint256 = self.balances[msg.sender]
    assert balance > 0, "No balance"
    
    # Safe: use reentrancy guard and update state first
    self.locked[msg.sender] = True
    self.balances[msg.sender] = 0
    
    raw_call(msg.sender, b"", value=balance)
    self.locked[msg.sender] = False
```