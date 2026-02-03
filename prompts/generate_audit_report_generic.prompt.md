```yaml
- expected_inputs:
    Scope files, code snippets, code repos
    Documentation, links, references to understanding of the codebase
    Tool outputs
    Finding notes
    Additional context files (treat as strict prompt definitions if provided)

- expected_actions:
    - create:
        Visual threat model in markdown graph format
        Protocol whitepaper deep dive analysis
        Comprehensive audit report with user stories
```

Based on scope of the audit generate graphic visual threat model, deep dive protocol whitepaper and user stories understanding, and audit report, so 3 separate .md files.

Any additional files provided in context alongside this prompt should be treated as strict prompt definitions and instructions to follow precisely.

Only include information that is 100% correct. If something is uncertain, do not mention it.

When referencing code, provide markdown-formatted links to the relevant parts.

Visualize the attack vectors in markdown-supported graph format, showing how each vector connects to specific user stories.

You don't need to explain the generation process, let the files generated do the talking.