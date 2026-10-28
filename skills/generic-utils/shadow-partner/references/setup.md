# Getting X API access working

## What the skill needs

An app's Consumer Key and Consumer Key Secret (OAuth 1.0a app keys). The scripts
mint an app-only bearer token from them. No user login, no callback URL.

## Where the scripts look

1. `X_API_KEY` and `X_API_SECRET` in the environment.
2. A 1Password item read through the `op` CLI, controlled by env vars so nothing
   personal is hard-coded:
   - `X_OP_ITEM` - item name or UUID (default "X API").
   - `X_OP_ACCOUNT` - the account to pass to `op` (optional; omitted if unset, so
     `op` uses its default account).

The key and secret may be stored either as URL/website fields or as ordinary item
fields. `xapi.py` reads both, trying the label pairs "Consumer Key" / "Consumer
Key Secret", then "API Key" / "API Key Secret", then "API Key" / "API Secret
Key". If `op` reports a field error, the values are under a label not in that
list - rename the fields or add the pair to `LABELS` in `xapi.py`. Follow the
`secure-1pass-access` skill to confirm the account and vault with the user once,
then read in a single call rather than prompting the fingerprint repeatedly.

## Getting keys from scratch

1. Sign in at <https://developer.x.com/en/portal/dashboard>.
2. Create a Project, then an App inside that Project.
3. On the app's "Keys and tokens" tab, generate the Consumer Keys (API Key and
   Secret). Copy both immediately - the secret is shown once.
4. Put them in 1Password as above, or export them in your shell.
5. Add pay-per-use credits in the portal, or every call returns `402`.

## The trap that costs an hour

An app created outside a Project authenticates fine - the token endpoint returns a
bearer token - and then every single v2 endpoint returns:

```
403 {"reason":"client-not-enrolled","detail":"...must use keys and tokens from
a developer App that is attached to a Project..."}
```

A working token proves nothing. If you see this, attach the app to a Project in
the portal (or make a new app inside one). `xapi.py` detects this case and says so
rather than printing a raw 403.

## What app-only keys cannot do

- `liking_users` (who liked a post) returns `403 Unsupported Authentication`. It
  needs an OAuth 2.0 user-context token, which means a browser authorization flow.
  Like-level attribution is out of reach for this skill; ask the user to authorize
  the app themselves if they really need it.
- Impressions for anyone else's posts. `impression_count` comes back only on the
  authenticated account's own posts, at any tier.
- The Highlights tab. There is no endpoint for it. The skill substitutes top posts
  by engagement and says so.

## Pricing, as of the last check

| Read | Price |
|---|---|
| post | $0.005 each returned |
| user | $0.010 each returned |

Engagement counts (likes, retweets, replies, quotes) ride along free inside a post
read. The user-timeline endpoint stops at the most recent 3,200 posts, replies and
retweets included, so a two-year window is not reachable for heavy posters -
full-archive search is a higher tier.
