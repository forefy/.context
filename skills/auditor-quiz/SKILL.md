---
name: auditor-quiz
description: Generate and administer interactive knowledge quizzes for security auditors based on repository documentation and code. Use when an auditor needs to be tested on their understanding of a codebase, protocol mechanics, security considerations, potential vulnerabilities, or core functionality. Triggers include requests like "quiz me on", "test my knowledge", "generate a quiz", or when preparing for security audits and code reviews.
---

# Auditor Quiz Skill

Generate focused, security-oriented quizzes to test auditor understanding of codebases, protocols, and documentation.

## Overview

This skill creates 8-10 question quizzes that focus on:
- Protocol/system understanding and core mechanisms
- Weakness points and potential vulnerabilities
- Security considerations and attack vectors
- Core functionality and critical code paths

Questions are generated from repository documentation (README, docs/, whitepapers, specifications, inline comments) and presented interactively with immediate feedback.

## Workflow

1. **Identify documentation sources**
   - Search for documentation files: `*.md`, `README*`, `docs/*`, `*.sol` (comments), `*.rs` (comments), etc.
   - Prioritize: security docs, architecture docs, README, specification files
   - Use grep/glob to find relevant files efficiently

2. **Analyze documentation**
   - Read and synthesize key information about:
     - Core protocol/system mechanics
     - Security assumptions and trust boundaries
     - Known edge cases or limitations
     - Critical functions and state transitions
     - Potential attack vectors or vulnerability areas
   
3. **Generate quiz questions**
   - Create 8-10 questions (mix of multiple choice, true/false)
   - Follow guidelines in `references/question-types.md`
   - Focus on security-critical aspects and deep understanding
   - Balance difficulty: 2-3 easy, 4-5 medium, 2-3 hard questions
   - Include specific references (line numbers, function names)
   - Store questions in memory (not in files)
   
4. **Run the quiz conversationally**
   - Present questions ONE AT A TIME in the conversation
   - Format clearly with question number, text, and answer options
   - WAIT for the user's answer in their next message
   - After receiving answer, provide immediate feedback:
     - ✅ CORRECT or ❌ INCORRECT
     - Show correct answer if wrong
     - Provide detailed explanation
     - Show current score (e.g., "Score: 3/5")
   - Continue to next question only after user responds
   - Track score throughout
   - Display final results at the end with percentage and feedback
   
5. **Important: Conversational Mode**
   - Do NOT use terminal scripts, bash sessions, or file-based quiz systems
   - Present each question directly in your response
   - Use the `ask_user` tool if helpful for getting answers
   - Keep the interaction natural and conversational

## Question Generation Guidelines

### Focus Areas

**Protocol Understanding** (2-3 questions):
- How core mechanisms work
- State transitions and workflows
- Design rationale

**Weakness Points** (2-3 questions):
- Known edge cases
- Potential attack vectors
- Boundary conditions

**Security Considerations** (2-3 questions):
- Access controls
- Trust assumptions
- Input validation
- Privilege boundaries

**Core Functionality** (1-2 questions):
- Main entry points
- Critical algorithms
- Key data structures

### Quality Standards

- **Specific**: Reference actual code (function names, line numbers)
- **Relevant**: Focus on audit-critical aspects
- **Clear**: Avoid ambiguity in questions and answers
- **Educational**: Explanations should teach, not just confirm
- **Deep**: Test understanding over memorization

Consult `references/question-types.md` for detailed examples and patterns.

## Resources

- **references/question-types.md** - Question format guidelines, examples, and best practices

## Tips

- When documentation is extensive (>10 files), prioritize security-relevant docs first
- Include code references in explanations (e.g., "line 142", "deposit() function")
- Present questions one at a time, waiting for user response between each
- Keep conversational flow natural - don't use scripts or terminal sessions
- Track score internally and display after each question
