# CONTEXT MAIN
From the moment you read this context file, you must adjust your purpose to be aware of and apply any referenced context files in a given prompt.

Context files are identified by their .ctx.md extension.
Whenever a .ctx.md file is referenced in a prompt, you must pay extra attention and extract relevant instructions from it.
These files contain unordered Markdown, meaning their structure is not hierarchical—you must read and interpret them as guidelines to modify your response accordingly.

Treat this file (general.ctx.md) as a root context, providing high-level guidelines for handling all context files.
Whenever a prompt includes references to one or more .ctx.md files, ensure their instructions influence your response accordingly.
Always prioritize the instructions within the referenced .ctx.md files and modify your response based on their directives.

General knowledge collection should also look, when uncertain, for files within whitepapers/ directory to obtain whitepaper or developer information for better quality answers.

Context files modify, extend, or constrain responses based on user needs.
If multiple .ctx.md files are referenced, combine their relevant details to tailor your response properly.
This file itself is a context file, meaning its principles apply just like any other .ctx.md file.