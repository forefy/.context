# FV-SOL-2-C3 Rounding

## TLDR

Solidity rounds down in integer division, which can lead to small precision losses that add up over multiple calculations.

This is particularly problematic in contracts dealing with revenue sharing, staking, or rewards distribution, where precision is critical.

## Game

In this contract, the `allocateShare` function calculates a recipient's share based on `totalFunds`, `recipientShares`, and `totalShares`

Look for uneven divisions.

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract SharesCalculationGame {
    uint256 public totalShares;
    uint256 public totalFunds;

    mapping(address => uint256) public shares;

    constructor(uint256 _totalShares) {
        totalShares = _totalShares;
    }

    function depositFunds() public payable {
        totalFunds += msg.value;
    }

    function allocateShare(address recipient, uint256 recipientShares) public {
        require(recipientShares <= totalShares, "Not enough shares available");

        uint256 allocation = (totalFunds * recipientShares) / totalShares;
        require(allocation <= totalFunds, "Allocation exceeds funds");

        shares[recipient] += recipientShares;
        totalFunds -= allocation;

        (bool success, ) = payable(recipient).call{value: allocation}("");
        require(success, "Transfer failed");
    }
}


```


### Hint 1
Solidity's integer division truncates decimals, which can lead to rounding issues in share calculations.

When `totalShares` is much larger than `recipientShares`, or doesn’t divide `totalFunds` evenly, think about how `(totalFunds * recipientShares) / totalShares` might round down and lose precision


### Hint 2
Examine how repeated calls to `allocateShare` might cause the total allocated funds to differ from `totalFunds`, especially in cases where small precision errors accumulate.


### Solution
```solidity
function allocateShare(address recipient, uint256 recipientShares) public {
    require(recipientShares <= totalShares, "Not enough shares available");

    // Fix: Apply a scaling factor to increase precision in calculations
    uint256 scaledTotalFunds = totalFunds * 10**18;
    uint256 allocation = (scaledTotalFunds * recipientShares) / totalShares / 10**18;

    require(allocation <= totalFunds, "Allocation exceeds funds");

    shares[recipient] += recipientShares;
    totalFunds -= allocation;

    (bool success, ) = payable(recipient).call{value: allocation}("");
    require(success, "Transfer failed");
}

```


