# FV-SOL-1-C6 Read-Only

## TLDR

**Read-only reentrancy** exploits functions that only perform "view" operations (i.e., don’t directly change state) but still affect the contract's behavior based on inconsistent state.

While such functions don’t modify storage, they may still provide inaccurate or exploitable information if they rely on external contract calls that can reenter and manipulate state elsewhere.

## Game

Think about what would happen if `msg.sender` is a contract that re-enters `getPrizeEligibility` via a fallback function during the call to `claimPrize`

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract ReadOnlyReentrancyGame {
    mapping(address => uint256) public balances;
    bool public prizeClaimed = false;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function getPrizeEligibility() public view returns (bool) {
        // Checks if the user has a balance and the prize is not yet claimed
        return (balances[msg.sender] >= 1 ether && !prizeClaimed);
    }

    function claimPrize() public {
        require(getPrizeEligibility(), "Not eligible for prize");
        prizeClaimed = true;
        (bool success, ) = msg.sender.call{value: 1 ether}("");
        require(success, "Transfer failed");
    }
}

```


### Hint 1
Notice that `getPrizeEligibility` is a view function, meaning it doesn’t directly modify state.

However, read-only reentrancy can happen if `msg.sender` can re-enter the view function during `claimPrize` to get outdated state information


### Hint 2
Think about whether `balances[msg.sender]` is updated _before_ the external call. If `dynamicPayout` is reentered, would the balance deduction prevent repeated calls, or is there a way to exploit this order?


### Solution
```solidity
function claimPrize() public {
    require(balances[msg.sender] >= 1 ether, "Insufficient balance");
    require(!prizeClaimed, "Prize already claimed");

    // Fix: Set prizeClaimed to true immediately to prevent reentrancy
    prizeClaimed = true;

    (bool success, ) = msg.sender.call{value: 1 ether}("");
    require(success, "Transfer failed");
}
```


