# FV-VYP-7-C1 Transaction Order Dependencies

## Bad

```vyper
# @version ^0.3.0

price: public(uint256)
owner: public(address)

@external
def __init__():
    self.owner = msg.sender
    self.price = 1000000000000000000  # 1 ETH

@external
@payable
def purchase():
    # Vulnerable: price can be front-run and changed
    assert msg.value >= self.price, "Insufficient payment"
    # Transfer ownership or tokens

@external
def update_price(new_price: uint256):
    assert msg.sender == self.owner, "Only owner"
    # Vulnerable: owner can front-run purchases with price increases
    self.price = new_price
```

## Good

```vyper
# @version ^0.3.0

price: public(uint256)
owner: public(address)
price_lock_until: public(uint256)

@external
def __init__():
    self.owner = msg.sender
    self.price = 1000000000000000000  # 1 ETH

@external
@payable
def purchase(max_price: uint256):
    # Safe: user specifies maximum acceptable price
    assert msg.value >= self.price, "Insufficient payment"
    assert self.price <= max_price, "Price too high"
    # Transfer ownership or tokens

@external
def update_price(new_price: uint256):
    assert msg.sender == self.owner, "Only owner"
    # Safe: price changes have a time delay
    assert block.timestamp >= self.price_lock_until, "Price locked"
    self.price = new_price
    self.price_lock_until = block.timestamp + 3600  # 1 hour delay
```