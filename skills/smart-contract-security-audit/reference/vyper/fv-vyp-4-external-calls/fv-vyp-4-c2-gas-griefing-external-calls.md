# FV-VYP-4-C2 Gas Griefing via External Calls

## Bad

```vyper
# @version ^0.3.0

recipients: public(DynArray[address, 100])

@external
def distribute_rewards():
    reward: uint256 = self.balance / len(self.recipients)
    
    for recipient in self.recipients:
        # Vulnerable: using all available gas for each call
        raw_call(recipient, b"", value=reward)
```

## Good

```vyper
# @version ^0.3.0

recipients: public(DynArray[address, 100])

@external
def distribute_rewards():
    reward: uint256 = self.balance / len(self.recipients)
    
    for recipient in self.recipients:
        # Safe: limit gas to prevent griefing
        success: bool = raw_call(
            recipient, 
            b"", 
            value=reward, 
            gas=2300,  # Limit gas to prevent reentrancy and griefing
            revert_on_failure=False
        )
        # Continue even if one transfer fails
```