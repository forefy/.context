# FV-VYP-6-C1 Predictable Random Number Generation

## Bad

```vyper
# @version ^0.3.0

participants: public(DynArray[address, 100])
winner: public(address)

@external
def enter_lottery():
    self.participants.append(msg.sender)

@external
def draw_winner():
    # Vulnerable: predictable randomness
    random_index: uint256 = block.timestamp % len(self.participants)
    self.winner = self.participants[random_index]

@external
def simple_coin_flip() -> bool:
    # Vulnerable: miners can influence block hash
    return convert(blockhash(block.number - 1), uint256) % 2 == 0
```

## Good

```vyper
# @version ^0.3.0

participants: public(DynArray[address, 100])
winner: public(address)
random_seed: uint256
commit_reveal_phase: public(bool)
commits: HashMap[address, bytes32]

@external
def commit_random(commitment: bytes32):
    # Safe: commit-reveal scheme
    assert self.commit_reveal_phase, "Not in commit phase"
    self.commits[msg.sender] = commitment

@external
def reveal_and_draw(nonce: uint256):
    # Safe: reveal phase with external randomness
    assert not self.commit_reveal_phase, "Still in commit phase"
    expected_commit: bytes32 = keccak256(concat(convert(msg.sender, bytes32), convert(nonce, bytes32)))
    assert self.commits[msg.sender] == expected_commit, "Invalid reveal"
    
    # Combine multiple sources of entropy
    self.random_seed = keccak256(concat(
        convert(self.random_seed, bytes32),
        convert(nonce, bytes32),
        convert(block.timestamp, bytes32)
    ))
    
    random_index: uint256 = convert(self.random_seed, uint256) % len(self.participants)
    self.winner = self.participants[random_index]
```