---
name: secure-1pass-access
description: Let the agent access local 1pass CLI credentials, without compromising security standards
---

1Password CLI (op) lets you access secrets and manage your account from your terminal and scripts. Install via `brew install 1password-cli` or `winget install 1password-cli`.

When an agent is given access to 1pass it needs to only read what the user wants, although the user don't necessarily know all details. to make the search seamless for the user we confirm that we know the account, and vault he wants to get the data from.

It could be that the item in the vault isn't accurate or it's multiple items, in which case we want to suggest a search query to then use via the op cli to match all at once and store them for the session only. this is because everytime we access a read 1password auto-opens a prompt requiring a fingerprint to access, which can be annoying if requested a lot.

Due to above we really prefer to do a 1-shot retreival for the entire session's purposes, to not depend on the user more than this 1/2 call.
