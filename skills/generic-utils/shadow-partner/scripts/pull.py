#!/usr/bin/env python3
"""Pull a persona's original posts for the alpha mining pass.

    python3 pull.py <handle> [--years 2] [--cap 20] [--out out]

Writes out/shadow_<handle>/posts.json - every post with its engagement metrics -
and prints the top posts by engagement, which is the closest thing the API has
to the Highlights tab (there is no Highlights endpoint).

Retweets and replies are excluded: they cost the same per post and mostly carry
other people's words.
"""
import argparse, json, os, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from xapi import Api, POST_READ, die, money  # noqa: E402

CEILING = 3200


def engagement(t):
    m = t["public_metrics"]
    return m["like_count"] + m["retweet_count"] + m["reply_count"] + m["quote_count"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("handle")
    p.add_argument("--years", type=float, default=2.0)
    p.add_argument("--cap", type=float, default=20.0, help="hard spend ceiling in USD")
    p.add_argument("--out", default="out")
    a = p.parse_args()

    handle = a.handle.lstrip("@")
    api = Api()
    u = api.user(handle)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=a.years * 365.25)).date().isoformat()
    print(f"@{u['username']} - originals since {cutoff} (cap {money(a.cap)})")

    posts, token, hit_cap = [], None, False
    while True:
        # note_tweet carries the untruncated body of long posts; without it ~40%
        # of a long-form poster's text arrives cut at 280 characters.
        params = {"max_results": "100", "exclude": "retweets,replies",
                  "tweet.fields": "created_at,public_metrics,entities,conversation_id,note_tweet"}
        if token:
            params["pagination_token"] = token
        d = api.get(f"/2/users/{u['id']}/tweets", params)
        if "_error" in d:
            print(f"    ! timeline read failed: {d.get('_body','')[:120]}")
            break
        batch = d.get("data", [])
        api.post_reads += len(batch)
        reached_cutoff = False
        for t in batch:
            if t["created_at"][:10] < cutoff:
                reached_cutoff = True
                continue
            m = t["public_metrics"]
            full = (t.get("note_tweet") or {}).get("text") or t["text"]
            posts.append({
                "id": t["id"], "date": t["created_at"][:10], "text": full,
                "likes": m["like_count"], "rt": m["retweet_count"],
                "replies": m["reply_count"], "quotes": m["quote_count"],
                "engagement": engagement(t),
                "urls": [e.get("expanded_url") for e in
                         t.get("entities", {}).get("urls", []) if e.get("expanded_url")],
                "link": f"https://x.com/{u['username']}/status/{t['id']}",
            })
        print(f"    {len(posts)} posts kept · {api.post_reads} read · {money(api.spend)}",
              flush=True)
        if api.spend > a.cap:
            hit_cap = True
            print(f"    ! hit the {money(a.cap)} cap - stopping here.")
            break
        token = d.get("meta", {}).get("next_token")
        if reached_cutoff or not token or not batch:
            break
        if api.post_reads >= CEILING:
            print(f"    ! reached the {CEILING:,}-post ceiling - the API goes no further back.")
            break

    if not posts:
        die("no posts in the window.")

    posts.sort(key=lambda x: x["date"], reverse=True)
    outdir = os.path.join(a.out, f"shadow_{u['username']}")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "posts.json")
    with open(path, "w") as f:
        json.dump({"persona": u, "cutoff": cutoff, "count": len(posts),
                   "oldest": posts[-1]["date"], "newest": posts[0]["date"],
                   "hit_cap": hit_cap, "spend_usd": round(api.spend, 2),
                   "posts": posts}, f, indent=2)

    top = sorted(posts, key=lambda x: -x["engagement"])[:15]
    print(f"\n{len(posts)} originals · {posts[-1]['date']} -> {posts[0]['date']} · {money(api.spend)}")
    print(f"saved -> {path}\n")
    print("top posts by engagement (the de facto highlights):")
    for t in top:
        text = " ".join(t["text"].split())[:72]
        print(f"  {t['date']}  {t['engagement']:>5}  {text}")


if __name__ == "__main__":
    main()
