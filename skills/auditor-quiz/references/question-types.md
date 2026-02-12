# Question Types and Guidelines

## Question Categories

When generating quiz questions, focus on these critical areas:

### 1. Protocol Understanding
- Core mechanisms and workflows
- State transitions and lifecycle
- Key invariants and assumptions
- Design rationale and tradeoffs

### 2. Weakness Points
- Known attack vectors
- Edge cases and boundary conditions
- Potential exploit scenarios
- Mitigation strategies

### 3. Security Considerations
- Access control mechanisms
- Input validation patterns
- Trust boundaries
- Cryptographic operations
- Privilege escalation risks

### 4. Core Functionality
- Main entry points
- Critical data structures
- Key algorithms
- Integration points
- Dependencies and assumptions

## Question Formats

### Multiple Choice (Preferred for complex concepts)
- 4 options (A, B, C, D)
- One clearly correct answer
- Plausible distractors that test understanding
- Focus on "why" and "how" rather than simple facts

**Example:**
```json
{
  "question": "What happens if a user calls withdraw() before the timelock period expires?",
  "type": "multiple_choice",
  "options": [
    "The transaction reverts with a TimelockNotExpired error",
    "The withdrawal succeeds with a reduced amount",
    "The transaction succeeds but emits a warning event",
    "The funds are sent to a penalty address"
  ],
  "correct_answer": "A",
  "explanation": "The require(block.timestamp >= unlockTime) check on line 142 ensures transactions revert if called before the timelock expires, preventing premature withdrawals."
}
```

### True/False (Best for testing assumptions)
- Clear statement that is unambiguously true or false
- Should test critical understanding or common misconceptions

**Example:**
```json
{
  "question": "The contract allows the owner to pause all user withdrawals indefinitely without any time limit.",
  "type": "true_false",
  "options": ["True", "False"],
  "correct_answer": "B",
  "explanation": "False. The pauseWithdrawals() function includes a MAX_PAUSE_DURATION constant (72 hours) to prevent indefinite pausing, protecting user funds from admin abuse."
}
```

### Short Answer (For specific technical details)
- Requires recalling specific function names, values, or mechanisms
- Tests precise knowledge of implementation

**Example:**
```json
{
  "question": "What modifier is used to restrict administrative functions to the owner?",
  "type": "short_answer",
  "correct_answer": "onlyOwner",
  "explanation": "The onlyOwner modifier checks that msg.sender == owner before allowing execution of admin functions."
}
```

## Difficulty Balance

Distribute questions across difficulty levels:
- **2-3 Easy**: Basic concepts, main functionality
- **4-5 Medium**: Interactions, edge cases, security patterns
- **2-3 Hard**: Subtle vulnerabilities, complex scenarios, attack vectors

## Quality Guidelines

1. **Specificity**: Questions should reference actual code, not generic concepts
2. **Relevance**: Focus on security-critical and audit-relevant aspects
3. **Clarity**: Avoid ambiguous wording
4. **Learning**: Explanations should add value and cite specific lines/functions
5. **Depth**: Test understanding, not memorization
