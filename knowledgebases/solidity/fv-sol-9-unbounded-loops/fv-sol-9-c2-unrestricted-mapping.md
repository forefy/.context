# FV-SOL-9-C2 Unrestricted Mapping

## TLDR

Solidity mappings do not provide a way to iterate over keys natively. However, if developers use an array to track mapping keys for iteration, looping through the keys can lead to unbounded loops if the array grows indefinitely

## Game

If this auxiliary array grows without restriction, what will looping over it do?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract UnrestrictedMappingGame {
    mapping(address => uint256) public balances;
    address[] public users;

    // Add or update a user's balance
    function setBalance(address user, uint256 amount) public {
        if (balances[user] == 0) {
            users.push(user);
        }
        balances[user] = amount;
    }

    // Sum up all balances
    function totalBalances() public view returns (uint256) {
        uint256 total = 0;
        for (uint256 i = 0; i < users.length; i++) {
            total += balances[users[i]];
        }
        return total;
    }
}
```


### Hint 1
Consider how you can limit the size of the `users` array to ensure predictable gas consumption for functions like `totalBalances`.


### Hint 2
Think about how precomputing or chunking operations might help avoid the need for full iteration in a single transaction.


### Solution
```solidity
contract UnrestrictedMappingGame {
    mapping(address => uint256) public balances;
    address[] public users;

    uint256 public maxUsers = 1000; // Fix: Restrict the maximum number of users

    function setBalance(address user, uint256 amount) public {
        if (balances[user] == 0) {
            require(users.length < maxUsers, "User limit reached"); // Fix: Enforce user limit
            users.push(user);
        }
        balances[user] = amount;
    }

    function totalBalances(uint256 start, uint256 end) public view returns (uint256) {
        require(end > start && end <= users.length, "Invalid range");
        uint256 total = 0;
        for (uint256 i = start; i < end; i++) {
            total += balances[users[i]];
        }
        return total;
    }
}
```


