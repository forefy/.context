# FV-VYP-3-C1 Missing Owner Checks

## Bad

```vyper
# @version ^0.3.0

owner: public(address)
paused: public(bool)

@external
def __init__():
    self.owner = msg.sender

@external
def pause():
    # Vulnerable: anyone can pause the contract
    self.paused = True

@external
def emergency_withdraw():
    # Vulnerable: anyone can drain the contract
    raw_call(msg.sender, b"", value=self.balance)
```

## Good

```vyper
# @version ^0.3.0

owner: public(address)
paused: public(bool)

@external
def __init__():
    self.owner = msg.sender

@external
def pause():
    # Safe: only owner can pause
    assert msg.sender == self.owner, "Only owner"
    self.paused = True

@external
def emergency_withdraw():
    # Safe: only owner can withdraw
    assert msg.sender == self.owner, "Only owner"
    raw_call(msg.sender, b"", value=self.balance)
```