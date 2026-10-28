#!/usr/bin/env python3
"""Shared X API plumbing for shadow-partner: credentials, token, GET, spend.

Credentials, in order:
  1. X_API_KEY / X_API_SECRET in the environment.
  2. A 1Password item, read through the `op` CLI. Which item (and which account)
     is controlled by env vars so nothing personal is baked into this file:
         X_OP_ITEM     item name or UUID      (default "X API")
         X_OP_ACCOUNT  account to pass to op  (optional; omitted if unset)
     The consumer key and secret may be stored either as URL/website fields or
     as ordinary item fields; both are searched, by the labels in LABELS below.
     Follow the repo's `secure-1pass-access` skill for the one-shot retrieval
     pattern (confirm the account and vault with the user once, then read).
"""
import base64, json, os, subprocess, sys, time
import urllib.error, urllib.parse, urllib.request

API = "https://api.twitter.com"
POST_READ = 0.005
USER_READ = 0.010
OP_ITEM = os.environ.get("X_OP_ITEM", "X API")
OP_ACCOUNT = os.environ.get("X_OP_ACCOUNT")  # None -> op uses its default account
# (key label, secret label) pairs to try, in order.
LABELS = [("Consumer Key", "Consumer Key Secret"),
          ("API Key", "API Key Secret"),
          ("API Key", "API Secret Key")]


def die(msg, code=1):
    print(f"\nERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def money(x):
    return f"${x:,.2f}"


def _op_fields(item_json):
    """All (label -> value) pairs in an op item, from both urls and fields."""
    out = {}
    for u in item_json.get("urls", []):
        if u.get("label"):
            out[u["label"]] = u.get("href")
    for f in item_json.get("fields", []):
        if f.get("label") and f.get("value"):
            out.setdefault(f["label"], f["value"])
    return out


def credentials():
    key, secret = os.environ.get("X_API_KEY"), os.environ.get("X_API_SECRET")
    if key and secret:
        return key, secret
    cmd = ["op", "item", "get", OP_ITEM, "--format", "json"]
    if OP_ACCOUNT:
        cmd += ["--account", OP_ACCOUNT]
    try:
        raw = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        die("no X_API_KEY/X_API_SECRET and the 1Password CLI (op) is not installed.\n"
            "See references/setup.md.")
    if raw.returncode != 0:
        die(f'1Password lookup for item "{OP_ITEM}" failed: {raw.stderr.strip()[:200]}\n'
            "Set X_OP_ITEM / X_OP_ACCOUNT, or see references/setup.md.")
    fields = _op_fields(json.loads(raw.stdout))
    for key_label, secret_label in LABELS:
        key, secret = fields.get(key_label), fields.get(secret_label)
        if key and secret:
            return key, secret
    die(f'the "{OP_ITEM}" item has no recognised key/secret fields '
        f"(looked for {', '.join(k for k, _ in LABELS)}).\nSee references/setup.md.")


class Api:
    """One bearer token, a request helper, and a running spend tally."""

    def __init__(self):
        key, secret = credentials()
        basic = base64.b64encode(f"{key}:{secret}".encode()).decode()
        req = urllib.request.Request(
            f"{API}/oauth2/token", data=b"grant_type=client_credentials",
            headers={"Authorization": f"Basic {basic}",
                     "Content-Type": "application/x-www-form-urlencoded"})
        try:
            self.bearer = json.load(urllib.request.urlopen(req))["access_token"]
        except urllib.error.HTTPError as e:
            die(f"could not mint a bearer token (HTTP {e.code}): {e.read().decode()[:200]}\n"
                "The keys are wrong or revoked -- see references/setup.md.")
        self.post_reads = 0
        self.user_reads = 0

    @property
    def spend(self):
        return self.post_reads * POST_READ + self.user_reads * USER_READ

    def get(self, path, params):
        url = f"{API}{path}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.bearer}"})
        for attempt in range(4):
            try:
                return json.load(urllib.request.urlopen(req))
            except urllib.error.HTTPError as e:
                body = e.read().decode()[:300]
                if e.code == 429:
                    nap = 60 * (attempt + 1)
                    print(f"    ... rate limited, waiting {nap}s", flush=True)
                    time.sleep(nap)
                    continue
                if e.code == 402:
                    die("402 Payment Required -- API credits are gone. Top up in the portal.")
                if e.code == 401:
                    die("401 Unauthorized -- the keys are no longer valid.")
                if e.code == 403 and "client-not-enrolled" in body:
                    die("403 client-not-enrolled -- the app behind these keys is not attached "
                        "to a Project in the X developer portal. See references/setup.md.")
                return {"_error": e.code, "_body": body}
        return {"_error": 429, "_body": "gave up after retries"}

    def user(self, handle):
        d = self.get(f"/2/users/by/username/{handle}",
                     {"user.fields": "public_metrics,name,description,created_at,pinned_tweet_id"})
        if "data" not in d:
            die(f"could not resolve @{handle}: {json.dumps(d)[:200]}")
        self.user_reads += 1
        return d["data"]
