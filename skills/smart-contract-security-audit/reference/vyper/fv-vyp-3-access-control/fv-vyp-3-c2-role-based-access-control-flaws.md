# FV-VYP-3-C2 Role-Based Access Control Flaws

## Bad

```vyper
# @version ^0.3.0

admin: public(address)
moderators: public(HashMap[address, bool])

@external
def __init__():
    self.admin = msg.sender

@external
def add_moderator(moderator: address):
    # Vulnerable: any moderator can add other moderators
    assert self.moderators[msg.sender], "Not a moderator"
    self.moderators[moderator] = True

@external
def remove_funds(amount: uint256):
    # Vulnerable: moderators can drain funds
    assert self.moderators[msg.sender], "Not a moderator"
    raw_call(msg.sender, b"", value=amount)
```

## Good

```vyper
# @version ^0.3.0

admin: public(address)
moderators: public(HashMap[address, bool])

@external
def __init__():
    self.admin = msg.sender

@external
def add_moderator(moderator: address):
    # Safe: only admin can add moderators
    assert msg.sender == self.admin, "Only admin"
    self.moderators[moderator] = True

@external
def remove_funds(amount: uint256):
    # Safe: only admin can remove funds
    assert msg.sender == self.admin, "Only admin"
    raw_call(msg.sender, b"", value=amount)
```