# FV-SOL-5-C3 Improper State Transitions

## TLDR

A contract that has a specific progression (e.g., setup, running, paused) may mistakenly allow state-changing functions to execute out of order, leading to potential exploitation

## Game

`startGame` and `completeGame` are intended to control the game’s progress through its stages. However, due to an issue with the conditional logic in `completeGame`, the game can behave strangely. Can you spot the missing check?

## Sections
### Code
```solidity
pragma solidity ^0.8.0;

contract StateTransitionGame {
    enum GameState { NotStarted, InProgress, Completed }
    GameState public state;

    constructor() {
        state = GameState.NotStarted;
    }

    function startGame() public {
        require(state == GameState.NotStarted, "Game already started or completed");
        state = GameState.InProgress;
    }

    function completeGame() public {
        state = GameState.Completed;
    }
}
```


### Hint 1
Look at the condition in `completeGame`.

Does it ensure that the game can only transition to `Completed` if it is currently `InProgress`?


### Hint 2
Consider how adding specific checks for each state transition might make the progression more controlled and prevent unexpected transitions.


### Solution
```solidity
function completeGame() public {
    require(state == GameState.InProgress, "Game must be in progress to complete"); // Fix: Check for InProgress state
    state = GameState.Completed;
}
```


