---
name: self-improve
description: Audit the conversation and the project for what could have gone better, then turn the generalizable lessons into committed improvements in the repo that hosts this skill. Use at the end of a task or conversation where the agent needed correction, repeated work, or took a longer path than necessary.
compatibility: skill file must be hosted on a git repository the agent can push to
---

# Purpose

Every run that invokes this skill should leave the next run better off than the last, by pushing what was learned back through the git source this skill is hosted at.

A lesson that stays in the conversation dies with the context window. A lesson written into a skill, a memory file, or a doc is the only kind that survives.

# Task definition

Audit the conversation and the project to find opportunities to improve how work is done here. Reflect on what was actually done, where it went wrong, and where it could have been done better.

What counts as an improvement:

- Continuation. A fresh context loading this repo to do the same task hits the same pitfalls unless something in the repo changes. Removing that repeat cost is the highest-value improvement available.
- Correct work rather than a workaround that grows more painful as the project does.
- Updates to project memory, skills and docs that generalize past the single case that prompted them.

What does not count:

- Changes that do not align with the project's long-term direction.
- Overbuilding something that does not merit it on a second look.
- Anything that trades away UX, security or reliability.

# Method

1. Review the conversation for corrections, retries, and dead ends. Each one is a candidate.
2. Separate the one-off from the generalizable. Only the generalizable is worth writing down.
3. Find the right home for each lesson. A rule about this repo belongs in the repo. A rule about how the agent works belongs in a skill. A fact that is not derivable from the code belongs in project memory.
4. Make the change, then verify it against the checks below before committing.

# Pre-commit checks

- Run the tests, and add tests covering new critical functionality.
- Security review the changed code and confirm no critical issue was introduced.
- Remove leftovers before committing: dead code, scratch scripts, sensitive data, and anything that pollutes history. History is effectively permanent, so this is both a professionalism and a security matter.
- Write short, accurate, human commit messages.
- Push to the working branch only with approval and at high confidence that nothing breaks.
- Planning notes, changelogs and scratch markdown files are often not useful to other developers. Ask the user before committing them, and delete them when they are not wanted.
- Before committing, check as far as possible that the change works and broke nothing.
- Commit no personal files, PII or names without explicit approval. Code must stay portable, with no hardcoded user paths or emails. Personal values belong in environment secrets if they belong anywhere.
- Replace em dashes with regular hyphens across the codebase, with one exception: database migration files such as `migrations/*.sql` are immutable once applied, and editing them changes their checksum and breaks deploys.
- Confirm any changed frontend component is screen-adaptive.
- Check that a fix made for the local environment also holds where it is deployed. A missing dependency resolved locally needs the deployment path to handle it too.
- Update the project's documentation where it is managed, whether that is in-repo docs or an external system.

# Git protocol

Work on the branch of the current context, including main, and push improvements back to that same branch. Use a pull request flow only when the user asked for a separate branch.

Raise improvements at the end of a task or conversation whenever there is something worth carrying forward. Land them with the user's approval rather than silently, so the user stays in control of what enters the repo.

# Result

Improvements are committed where the next run will actually load them, and the same correction does not have to be made twice.
