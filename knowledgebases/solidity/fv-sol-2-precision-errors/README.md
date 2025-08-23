# FV-SOL-2 Precision Errors

## TLDR

Precision errors arise when contracts mishandle decimal scaling or rounding in calculations, leading to inaccurate results

## Code

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableToken {
    string public name = "VulnerableToken";
    string public symbol = "VUL";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);

    constructor(uint256 initialSupply) {
        // Initialize total supply without accounting for decimals
        totalSupply = initialSupply;
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }

    // Mint function vulnerable to incorrect decimal handling
    function mint(uint256 amount) public {
        // Fails to scale by decimals, causing inflated supply
        totalSupply += amount;
        balanceOf[msg.sender] += amount;
        emit Transfer(address(0), msg.sender, amount);
    }
}

```

## Classifications

#### [fv-sol-2-c1-token-decimals.md](fv-sol-2-c1-token-decimals.md "mention")

#### [fv-sol-2-c2-floating-point.md](fv-sol-2-c2-floating-point.md "mention")

#### [fv-sol-2-c3-rounding.md](fv-sol-2-c3-rounding.md "mention")

#### [fv-sol-2-c4-division-by-zero.md](fv-sol-2-c4-division-by-zero.md "mention")

#### [fv-sol-2-c5-time-based.md](fv-sol-2-c5-time-based.md "mention")

## Mitigation Patterns

### FV-SOL-2-M1 Unit Testing on Edge Cases

Write tests for edge cases, such as small or very large values, fractions close to rounding boundaries, zero values, and more.

## Actual Occurrences

* [https://solodit.cyfrin.io/issues/h-4-victims-fund-can-be-stolen-due-to-rounding-error-and-exchange-rate-manipulation-sherlock-napier-git](https://solodit.cyfrin.io/issues/h-4-victims-fund-can-be-stolen-due-to-rounding-error-and-exchange-rate-manipulation-sherlock-napier-git)
* [https://solodit.cyfrin.io/issues/h-05-vault-treats-all-tokens-exactly-the-same-that-creates-huge-arbitrage-opportunities-code4rena-yaxis-yaxis-contest-git](https://solodit.cyfrin.io/issues/h-05-vault-treats-all-tokens-exactly-the-same-that-creates-huge-arbitrage-opportunities-code4rena-yaxis-yaxis-contest-git)