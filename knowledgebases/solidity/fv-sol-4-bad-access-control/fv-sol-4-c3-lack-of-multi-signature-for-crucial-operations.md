# FV-SOL-4-C3 Lack of Multi-Signature for Crucial Operations

## TLDR

If a critical function (like transferring large funds or changing important contract settings) is controlled by a single address (usually the contract owner), it creates a single point of failure.

## Game

Consider the risks associated with allowing a single administrator to have complete control over all contract funds. What might be a safer approach for sensitive operations like `withdrawAllFunds`?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract SingleAdminOperation {
    address public admin;
    uint256 public contractBalance;

    constructor() {
        admin = msg.sender;
    }

    function deposit() public payable {
        contractBalance += msg.value;
    }

    function withdrawAllFunds(address payable recipient) public {
        require(msg.sender == admin, "Only admin can withdraw funds");
        recipient.transfer(contractBalance);
        contractBalance = 0;
    }
}

```


### Hint 1
For highly sensitive actions, it’s often wise to have multiple parties involved. Think about how consensus could add security here.


### Hint 2
Consider if adding conditions or roles for more than one user might mitigate the risk of a single point of control.


### Solution
```solidity
mapping(address => bool) public approvers;
uint256 public approvalCount;
uint256 public requiredApprovals;

// Fix: Constructor now sets up initial approvers and required approvals
constructor(address[] memory initialApprovers, uint256 _requiredApprovals) {
    require(_requiredApprovals <= initialApprovers.length, "Invalid number of required approvals");
    for (uint256 i = 0; i < initialApprovers.length; i++) {
        approvers[initialApprovers[i]] = true;
    }
    requiredApprovals = _requiredApprovals;
    admin = msg.sender;
}

function approveWithdrawal() public {
    require(approvers[msg.sender], "Not authorized to approve");
    approvalCount += 1;
}

function withdrawAllFunds(address payable recipient) public {
    require(approvalCount >= requiredApprovals, "Not enough approvals");
    recipient.transfer(contractBalance);
    contractBalance = 0;
    approvalCount = 0; // Reset approval count after withdrawal
}
```


