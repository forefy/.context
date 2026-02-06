# FV-VYP-9-C1 Unbounded Loops

## Bad

```vyper
# @version ^0.3.0

participants: public(DynArray[address, 1000])
balances: public(HashMap[address, uint256])

@external
def distribute_rewards():
    reward_per_participant: uint256 = self.balance / len(self.participants)
    
    # Vulnerable: unbounded loop can cause gas limit issues
    for participant in self.participants:
        self.balances[participant] += reward_per_participant

@external
def remove_participant(target: address):
    new_participants: DynArray[address, 1000] = []
    
    # Vulnerable: loop over entire array to remove one element
    for participant in self.participants:
        if participant != target:
            new_participants.append(participant)
    
    self.participants = new_participants
```

## Good

```vyper
# @version ^0.3.0

participants: public(DynArray[address, 100])  # Limit array size
balances: public(HashMap[address, uint256])
participant_indices: HashMap[address, uint256]
distribution_index: public(uint256)

@external
def distribute_rewards_batch(batch_size: uint256):
    reward_per_participant: uint256 = self.balance / len(self.participants)
    end_index: uint256 = min(self.distribution_index + batch_size, len(self.participants))
    
    # Safe: process in batches to avoid gas limit
    for i in range(self.distribution_index, end_index):
        self.balances[self.participants[i]] += reward_per_participant
    
    self.distribution_index = end_index

@external
def remove_participant(target: address):
    target_index: uint256 = self.participant_indices[target]
    last_index: uint256 = len(self.participants) - 1
    
    # Safe: O(1) removal by swapping with last element
    if target_index != last_index:
        last_participant: address = self.participants[last_index]
        self.participants[target_index] = last_participant
        self.participant_indices[last_participant] = target_index
    
    self.participants.pop()
    self.participant_indices[target] = 0
```