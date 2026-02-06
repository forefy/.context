# FV-SOL-4 Bad Access Control

## TLDR

Improper access control can let unauthorized users access or modify restricted functionality

## Code

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BadAccessControl {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {}

    function withdraw() public {
        // No access control here, anyone can call this
        payable(msg.sender).transfer(address(this).balance);
    }
}
```

## Classifications

#### [fv-sol-4-c1-using-tx.origin-for-authorization.md](fv-sol-4-c1-using-tx.origin-for-authorization.md "mention")

#### [fv-sol-4-c2-unrestricted-role-assignment.md](fv-sol-4-c2-unrestricted-role-assignment.md "mention")

### Lack of Multi-Signature for Crucial Operations (FV-SOL-4-C3)

if a critical function (like transferring large funds or changing important contract settings) is controlled by a **single address** (usually the contract owner), it creates a **single point of failure**

## Mitigation Patterns

### Ownership Pattern (FV-SOL-4-M1)

The ownership pattern restricts critical functions to the contract owner, usually set during contract deployment. This is commonly achieved with an `onlyOwner` modifier

### Proper RBAC (FV-SOL-4-M2)

Role-Based Access Control allows defining multiple roles, each with specific permissions. For example, roles like `Admin`, `Minter`, or `Pauser` can be created, allowing more granular control

### Multi-Signature Approval (FV-SOL-4-M3)

Multi-sig patterns require multiple accounts to approve a critical action before it can be executed. This reduces the risk of unauthorized actions due to a compromised account

## Actual Occurrences

* [https://solodit.cyfrin.io/issues/h-02-eth-gets-locked-in-the-groupcoinfactory-contract-pashov-audit-group-none-groupcoin-markdown](https://solodit.cyfrin.io/issues/h-02-eth-gets-locked-in-the-groupcoinfactory-contract-pashov-audit-group-none-groupcoin-markdown)
