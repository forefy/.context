# Human instructions on setup required for this skill to be able to see google drive files

For security isolation, we do not want to give agents free access to roam around our google drive, instead - we can create a service account, and give it access to only what it needs to work on and nothing else.

1. Go to APIs & Services → Library and enable Google Drive API and Google Docs API
2. Go to IAM & Admin → Service Accounts → + Create Service Account
3. Give it a name (e.g. chainer-drive), skip optional role/user steps, click Done
4. Click the service account → Keys tab → Add Key → Create new key → JSON → Download → PLACE SOMEWHERE THIS SKILL CAN READ
5. Share an AI-ONLY Google Drive folder with the service account's email address (shown after connecting)
