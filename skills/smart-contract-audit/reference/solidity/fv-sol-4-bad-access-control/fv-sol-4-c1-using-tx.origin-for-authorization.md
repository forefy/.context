# FV-SOL-4-C1 Using tx.origin for Authorization

## TLDR

**Using `tx.origin` for authorization** is insecure because `tx.origin` includes the original external account that initiated the transaction, even if the transaction passed through multiple contracts.

This makes it vulnerable to phishing attacks where an attacker tricks a privileged user (like an admin) into calling a malicious contract, which then calls the vulnerable contract using `tx.origin` as authorization.

In such cases, `msg.sender` is a safer alternative for authorization, as it only represents the immediate caller of the function.

## Game

Find the bad access control implementation

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract TxOriginAuthGame {
    address public admin;

    constructor() {
        admin = msg.sender; // Set the deployer as admin
    }

    function restrictedAction() public view returns (string memory) {
        require(tx.origin == admin, "Only admin can call this function");
        return "Admin action performed!";
    }
}

```


### Hint 1
`tx.origin` represents the original external account that initiated the transaction, even if it goes through multiple contracts.

Think about what might happen if a malicious contract calls `restrictedAction` after being triggered by the admin.


### Hint 2
Using `msg.sender` instead of `tx.origin` provides safer access control since `msg.sender` only represents the immediate caller of the function, ensuring that only the admin can directly call `restrictedAction`


### Solution
```solidity
function restrictedAction() public view returns (string memory) {
    require(msg.sender == admin, "Only admin can call this function"); // Fix: Use msg.sender instead of tx.origin
    return "Admin action performed!";
}
```


