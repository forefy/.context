# FV-SOL-4-C2 Unrestricted Role Assignment

## TLDR

If a function to set an owner or assign roles is **public or lacks access control**, anyone can call it, potentially taking control of the contract

## Game

Your task is to identify how unauthorized users might exploit this contract to assign themselves privileged access. The `assignPrivilege` function seems simple, but there’s more to consider in how it’s secured.

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract RoleAssignmentGame {
    address public admin;
    mapping(address => bool) public privilegedUsers;

    constructor() {
        admin = msg.sender;
    }

    function assignPrivilege(address user) public {
        privilegedUsers[user] = true;
    }

    function restrictedFunction() public view returns (string memory) {
        require(privilegedUsers[msg.sender], "Access denied");
        return "Privileged access granted!";
    }
}
```


### Hint 1
When thinking about role assignment, consider who should ideally have control over this function and whether this is enforced here.


### Hint 2
Ask yourself if any user could call `assignPrivilege` and what might happen if they did so.


### Solution
```solidity
function assignPrivilege(address user) public {
    require(msg.sender == admin, "Only admin can assign privileges"); // Fix: access control
    privilegedUsers[user] = true;
}
```


