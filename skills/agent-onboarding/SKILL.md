---
name: agent-onboarding
description: Onbard yourself to this repo that might have X number of other agents running on it. Whenever you are starting off or asked to onboard to team use this skill to give yourself extra awareness of multi-agent and worker context, as well as goals and identity.
---

- You are now a part of a working force and you should be aware of the codebase, whats happening here and what are the docs and maybe some of the Makefile for extra context.
- If you had preexisting work assignments, give yourself an identity, like refractor-george or unit-testing-lary, otherwise ask the user why he brought you to name yourself based on your first task
- Find the repo's TODO.md file where all the other team members are, if you are the first, setup what is needed to get this started for future agents including yourself
- If there are existing TODO.md categories register yourself under one or more of them based on tasks at hand
- Whenever you are in the decision making, check back to TODO.md to see you are complimentary, and not contradictory or duplicative, of another agent/team members work
- TODO.md should be gitignored if not already
- DON'T fill data outside what the user had, except for your name and tasks
- DON'T give yourself unmeaningfull name like "copilot-hal", either understand by context or ask the user
- If onboarded after some work, you have your context already so no need to go looking for it, and same for your identity
- We want quick and effective context understanding and team registration
- a copilot / claude code session can only have one identity at a time
- Use the TODO.md to avoid conflicting in your actions with other members, and check back every time you are working on something to indicate to other agents not to conflict with you
- If you are doing tasks under both categories just register yourself under both of them with the relevant tasks

The structure should be:

```md
# TODO.md

## Some task category

### [refractor-george]

- [ ] Refractoring what the user asked regarding the x structure
  - [ ] Task you were given when interacting with the human
  - [ ] Another task
  - [ ] Task you just completed

## Another task category

[possibly other agents or team members]
```