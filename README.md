# Reusable Prompts for Smart Contract Auditing

<p align="center">
<img src="https://github.com/forefy/.context/raw/main/static/context.png" alt="Reusable Prompts for Smart Contract Auditing" title="Reusable Prompts for Smart Contract Auditing" width="450"/>
</p>

## What is this?
Not re-using LLM prompts in your auditing methodology is a waste of a technological edge.

In this repo I'm maintaining templates to get you started with reusable prompts in your smart contract audits.

It lets you reference this files from within your editor, not only saving you time in writing manually but mostly giving us auditors an opportunity to collaborate improve the baseline of how we use AI in our auditing flow.


## How to use
1. Use a reference-supporting IDE (VSCode + Copilot is my personal preference)
2. Inside the repo of the project you are currently auditing, run `git clone https://github.com/forefy/.context`
3. Open the AI chat, add relevant context for specific code sections as you go, and reference the markdown files in the context directory to your needs.
4. Personalize - adjust specifically for the project you're auditing, add refinements and specifics

## Modules list
| Prompt file                                                | Description                                                                                                             |
|------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| [discovery.ctx.md](discovery.ctx.md)                       | Helps with concise but technical overview of referenced code section, to help think learn and deduce low-hanging fruits |
| [fact_check.ctx.md](fact_check.ctx.md)                     | Anti-hallucination and attempts to disrupt truthness of potentially false finding assumptions                           |
| [finding.ctx.md](finding.ctx.md)                           | Takes converstion data or referenced code and outputs an official finding format out of it                              |
| [general.ctx.md](general.ctx.md)                           | Global overview context, trying to emphasize the purpose that we're currently in a smart contract audit mode            |
| [impact.ctx.md](impact.ctx.md)                             | Try to optimize or enhance finding impact information                                                                   |
| scope_info.ctx.md                                          | Corelate specific information about the scope of the audit or specific focus areas. File needs to be created manually   |
| [unit_test_awareness.ctx.md](unit_test_awareness.ctx.md)   | Learn from the unit tests to get a better clarity of what the code is expected to behave like                           |

## Contributing
Hoping for contributions for the generic layer - the one that we can all benefit, of course keep secret sauces for yourself! but everything else is highly welcomed here