---
name: context-window-to-skill
description: Takes the active conversation as reference to understand how a skill can be created, with all the lessons learned from the users need in the conversation.
---

# Use Case:
User had finished working on his feature or task successfully, but had to tweak lots of stuff in the behavior of the agent prior to completion - we now want to create a skill that in the next time will make this task a breeze

Steps:
1. Analyze conversation and understand fully what the user tried to achieve
2. Analyze where were the pitfalls, user frustrations, and what pre-information would have made the results quicker to get with the most quality
3. Print to the user 10 (or more) top items you think are the core points to base the new skill upon
4. Consult with the user if questions still remain
5. Create a skill and place it on the ~/.claude/skills/ directory. comply to agent skill format and [https://code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)

Results:
- Working new skill, that next time would do the job much better with all the tweaks needed to perfect it based on learned conversation and observation
- New skill should be reusable (e.g. think fixes also for future usecases other than the single one the user encountered)