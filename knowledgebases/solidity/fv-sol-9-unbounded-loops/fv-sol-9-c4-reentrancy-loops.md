# FV-SOL-9-C4 Reentrancy Loops

## TLDR

When a loop involves multiple calls to external contracts (e.g., `token.transfer()` or `someOtherContract.call()`), the gas cost becomes unpredictable and can be higher than expected due to the external call’s complexity.

## Game

You’ve discovered a contract designed to distribute funds across multiple recipients. But wait—what happens when one recipient is a contract with a fallback function that calls back into the fund distributor? Is the loop secure, or will it spin out of control?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract ReentrancyLoopsGame {
    mapping(address => uint256) public balances;

    // Distribute funds to an array of recipients
    function distributeFunds(address[] memory recipients, uint256[] memory amounts) public {
        require(recipients.length == amounts.length, "Mismatched inputs");

        for (uint256 i = 0; i < recipients.length; i++) {
            require(balances[msg.sender] >= amounts[i], "Insufficient balance");
            balances[msg.sender] -= amounts[i];
            payable(recipients[i]).transfer(amounts[i]);
        }
    }

    // Deposit funds
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
}

```


### Hint 1
What happens if a recipient’s contract has a fallback function that re-calls `distributeFunds` during the loop? Could the loop continue in an unexpected way?


### Hint 2
Consider how you might prevent a recipient’s contract from interfering with the loop’s execution.


### Solution
```solidity
function distributeFunds(address[] memory recipients, uint256[] memory amounts) public {
    require(recipients.length == amounts.length, "Mismatched inputs");

    for (uint256 i = 0; i < recipients.length; i++) {
        require(balances[msg.sender] >= amounts[i], "Insufficient balance");
        balances[msg.sender] -= amounts[i]; // Fix: Update state before external interaction
    }

    for (uint256 i = 0; i < recipients.length; i++) {
        // Fix: Perform external interaction in a separate loop to mitigate reentrancy
        payable(recipients[i]).transfer(amounts[i]);
    }
}
```


