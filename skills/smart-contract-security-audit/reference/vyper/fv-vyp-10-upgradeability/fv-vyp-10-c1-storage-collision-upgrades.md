# FV-VYP-10-C1 Storage Collision in Upgrades

## Bad

```vyper
# @version ^0.3.0
# Implementation V1

owner: public(address)
balance: public(uint256)

@external
def __init__():
    self.owner = msg.sender

# Implementation V2 - VULNERABLE
# @version ^0.3.0

owner: public(address)
total_supply: public(uint256)  # Storage collision! Was 'balance'
balance: public(uint256)       # Now at different slot

@external
def __init__():
    self.owner = msg.sender
```

## Good

```vyper
# @version ^0.3.0
# Implementation V1

owner: public(address)
balance: public(uint256)
# Reserve storage slots for future use
_reserved0: uint256
_reserved1: uint256
_reserved2: uint256

@external
def __init__():
    self.owner = msg.sender

# Implementation V2 - SAFE
# @version ^0.3.0

owner: public(address)
balance: public(uint256)       # Keep original layout
total_supply: public(uint256)  # Use reserved slot
_reserved1: uint256           # Still reserved
_reserved2: uint256           # Still reserved

@external
def __init__():
    self.owner = msg.sender
```