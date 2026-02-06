# FV-VYP-4-C1 Unchecked External Call Returns

## Bad

```vyper
# @version ^0.3.0

@external
def transfer_to_contract(target: address, amount: uint256):
    # Vulnerable: not checking if call succeeded
    raw_call(target, method_id("transfer(uint256)"), amount, max_outsize=0)

@external
def batch_transfer(recipients: DynArray[address, 10], amounts: DynArray[uint256, 10]):
    for i in range(len(recipients)):
        # Vulnerable: one failure doesn't stop the loop
        raw_call(recipients[i], b"", value=amounts[i])
```

## Good

```vyper
# @version ^0.3.0

@external
def transfer_to_contract(target: address, amount: uint256):
    # Safe: check return value and handle failure
    success: bool = raw_call(target, method_id("transfer(uint256)"), amount, max_outsize=0, revert_on_failure=False)
    assert success, "Transfer failed"

@external
def batch_transfer(recipients: DynArray[address, 10], amounts: DynArray[uint256, 10]):
    for i in range(len(recipients)):
        # Safe: check each call and revert on failure
        success: bool = raw_call(recipients[i], b"", value=amounts[i], revert_on_failure=False)
        assert success, "Transfer failed"
```