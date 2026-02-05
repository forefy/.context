# FV-SOL-1-C4 Cross Chain

## TLDR

**Cross-chain reentrancy** involves exploiting asynchronous transactions or inconsistencies between two blockchains that communicate with each other.

In this type of vulnerability, an attacker leverages the delay or difference in state updates across chains to manipulate the state on one chain based on outdated or unverified information from another chain.

## Game

Consider how an attacker might exploit this contract if they can control or manipulate the calls to `completeTransfer` through cross-chain messaging.

How could an attacker use reentrant calls from one chain to the other to alter the `balances` in unintended ways?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract CrossChainBridge {
    mapping(address => uint256) public balances;

    event TransferInitiated(address indexed user, uint256 amount, string targetChain);
    event TransferCompleted(address indexed user, uint256 amount);

    // Function to start transferring funds to another chain
    function initiateTransfer(uint256 amount, string memory targetChain) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        emit TransferInitiated(msg.sender, amount, targetChain);
        // Assume the amount is now locked, awaiting confirmation from the target chain
    }

    // Function to receive funds back from the other chain
    function completeTransfer(address user, uint256 amount) public {
        balances[user] += amount;
        emit TransferCompleted(user, amount);
    }
}
```


### Hint 1
Cross-chain reentrancy often involves delayed state changes and trust assumptions about calls between chains.

Look closely at `completeTransfer` and consider what happens if the function is called repeatedly or unexpectedly, especially if there’s no verification of the source


### Hint 2
Think about how an attacker could use `completeTransfer` to manipulate `balances` without sending actual funds from the other chain.

Since `balances[user]` is updated directly in `completeTransfer`, consider what could happen if they initiate a transfer and then repeatedly trigger `completeTransfer` from the "other chain."


### Solution
```solidity
function completeTransfer(address user, uint256 amount) public {
    require(isTrustedSource(msg.sender), "Untrusted source"); // Fix: Example verification
    require(!isProcessedTransaction(user, amount), "Already processed"); // Fix 2: Track processed transfers

    balances[user] += amount;
    markTransactionProcessed(user, amount); // Mark transaction as processed
    emit TransferCompleted(user, amount);
}

```


