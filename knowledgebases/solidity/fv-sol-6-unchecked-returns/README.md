# FV-SOL-6 Unchecked Returns

### TLDR

Failure to check returns is a surprising pitfall to many smart contracts. Not checking returns properly could cause unexpected behavior leading to security issues as a result.

## Code


```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableUncheckedCall {
    mapping(address => uint256) public balances;

    // Allows users to deposit Ether into the contract
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // Vulnerable withdraw function with an unchecked external call
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        balances[msg.sender] -= amount;

        // Unchecked call to send Ether to the sender
        // Vulnerability: If this call fails, the contract does not handle it,
        // resulting in potential issues for the user
        (bool success, ) = msg.sender.call{value: amount}("");
        
        // The return value of the call is unchecked, so the contract assumes the transfer succeeded
    }
}

```

## Classifications

#### [.](./ "mention")

#### [fv-sol-6-c2-unchecked-transfer-return.md](fv-sol-6-c2-unchecked-transfer-return.md "mention")

#### [fv-sol-6-c3-silent-fail.md](fv-sol-6-c3-silent-fail.md "mention")

#### [fv-sol-6-c4-false-positive-success-assumption.md](fv-sol-6-c4-false-positive-success-assumption.md "mention")

#### [fv-sol-6-c5-partial-execution-with-no-rollback.md](fv-sol-6-c5-partial-execution-with-no-rollback.md "mention")

#### [fv-sol-6-c6-false-contract-existence-assumption.md](fv-sol-6-c6-false-contract-existence-assumption.md "mention")

## Mitigation Patterns

### Checked Returns FV-SOL-6-M1)

It is generally a good strategy to ensure that all returns in your contract has at least minimal checks for validity, success and expected return values

### Checks-Effects-Interactions(FV-SOL-6-M2)

This pattern ensures that all internal changes are made (checks and effects) before any external calls are made, reducing reentrancy risks and ensuring contract state integrity before interactions

## Actual Occurrences

* [https://solodit.cyfrin.io/issues/m-11-unchecked-return-value-of-low-level-calldelegatecall-code4rena-nextgen-nextgen-git](https://solodit.cyfrin.io/issues/m-11-unchecked-return-value-of-low-level-calldelegatecall-code4rena-nextgen-nextgen-git)
* [https://solodit.cyfrin.io/issues/lack-of-contract-existence-check-on-delegatecall-may-lead-to-unexpected-behavior-trailofbits-yield-v2-pdf](https://solodit.cyfrin.io/issues/lack-of-contract-existence-check-on-delegatecall-may-lead-to-unexpected-behavior-trailofbits-yield-v2-pdf)
* [https://solodit.cyfrin.io/issues/h-03-result-of-transfer-transferfrom-not-checked-code4rena-spartan-protocol-spartan-protocol-contest-git](https://solodit.cyfrin.io/issues/h-03-result-of-transfer-transferfrom-not-checked-code4rena-spartan-protocol-spartan-protocol-contest-git)