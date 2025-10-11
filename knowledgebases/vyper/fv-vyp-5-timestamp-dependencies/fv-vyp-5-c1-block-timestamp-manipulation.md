# FV-VYP-5-C1 Block Timestamp Manipulation

## Bad

```vyper
# @version ^0.3.0

auction_end: public(uint256)
highest_bid: public(uint256)
highest_bidder: public(address)

@external
def __init__(duration: uint256):
    self.auction_end = block.timestamp + duration

@external
@payable
def bid():
    # Vulnerable: relying on exact timestamp comparison
    assert block.timestamp < self.auction_end, "Auction ended"
    assert msg.value > self.highest_bid, "Bid too low"
    
    self.highest_bid = msg.value
    self.highest_bidder = msg.sender

@external
def end_auction():
    # Vulnerable: miners can manipulate timestamp slightly
    assert block.timestamp >= self.auction_end, "Auction not ended"
    raw_call(self.highest_bidder, b"", value=self.highest_bid)
```

## Good

```vyper
# @version ^0.3.0

auction_end_block: public(uint256)
highest_bid: public(uint256)
highest_bidder: public(address)
AUCTION_DURATION: constant(uint256) = 28800  # ~8 hours in blocks

@external
def __init__():
    self.auction_end_block = block.number + AUCTION_DURATION

@external
@payable
def bid():
    # Safe: use block numbers instead of timestamps
    assert block.number < self.auction_end_block, "Auction ended"
    assert msg.value > self.highest_bid, "Bid too low"
    
    self.highest_bid = msg.value
    self.highest_bidder = msg.sender

@external
def end_auction():
    # Safe: block numbers are harder to manipulate
    assert block.number >= self.auction_end_block, "Auction not ended"
    raw_call(self.highest_bidder, b"", value=self.highest_bid)
```