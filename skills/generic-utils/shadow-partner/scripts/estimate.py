#!/usr/bin/env python3
"""Price a shadow-partner run before spending anything real.

Two measurements:
  lifetime rate - total posts / account age, from one profile read ($0.01)
  recent rate   - the span covered by a 20-post probe (about $0.10)

The recent rate is the one to quote; the lifetime rate catches accounts that
changed pace. Both include replies and retweets, so an originals-only pull
comes in under the quote.

    python3 estimate.py <handle> [--years 2]
"""
import argparse, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from xapi import Api, POST_READ, money  # noqa: E402

CEILING = 3200  # the user-timeline endpoint will not page past this


def main():
    p = argparse.ArgumentParser()
    p.add_argument("handle")
    p.add_argument("--years", type=float, default=2.0)
    p.add_argument("--probe", type=int, default=20,
                   help="posts to sample for the recent rate (min 5)")
    a = p.parse_args()

    api = Api()
    u = api.user(a.handle.lstrip("@"))
    m = u["public_metrics"]
    created = datetime.fromisoformat(u["created_at"].replace("Z", "+00:00"))
    age_years = max((datetime.now(timezone.utc) - created).days / 365.25, 0.1)
    lifetime_rate = m["tweet_count"] / age_years

    probe = api.get(f"/2/users/{u['id']}/tweets",
                    {"max_results": str(max(a.probe, 5)), "tweet.fields": "created_at"})
    batch = probe.get("data", [])
    api.post_reads += len(batch)
    recent_rate = None
    if len(batch) >= 2:
        newest = datetime.fromisoformat(batch[0]["created_at"].replace("Z", "+00:00"))
        oldest = datetime.fromisoformat(batch[-1]["created_at"].replace("Z", "+00:00"))
        span_days = max((newest - oldest).total_seconds() / 86400, 0.25)
        recent_rate = (len(batch) - 1) / span_days * 365.25

    print(f"\n@{u['username']} ({u.get('name','')}) - {m['followers_count']:,} followers")
    print(f"  joined {created.date()} · {m['tweet_count']:,} posts lifetime")
    print(f"\n  lifetime rate : {lifetime_rate:>7,.0f} posts/year")
    if recent_rate:
        print(f"  recent rate   : {recent_rate:>7,.0f} posts/year "
              f"(last {len(batch)} posts span {span_days:.1f} days)")

    rates = [r for r in (lifetime_rate, recent_rate) if r]
    lo, hi = min(rates) * a.years, max(rates) * a.years
    if recent_rate and span_days < 3:
        print("  (the probe lands inside a posting burst - treat the recent rate as a ceiling)")

    print(f"\n  projected for {a.years:g} years: {lo:,.0f}–{hi:,.0f} posts "
          f"(replies and retweets included)")
    # The endpoint stops at CEILING posts, so no projection can cost more than that.
    billable_hi = min(hi, CEILING)
    print(f"  cost at ${POST_READ:.3f}/post: {money(lo * POST_READ)}–"
          f"{money(billable_hi * POST_READ)}")
    print(f"  originals only, roughly a third to a half of that: "
          f"{money(lo * POST_READ / 3)}–{money(billable_hi * POST_READ / 2)}")

    if hi > CEILING:
        reach = CEILING / max(rates) * 12
        print(f"\n  ! past the {CEILING:,}-post ceiling. The timeline endpoint stops there, "
              f"so this pull reaches back about {reach:.0f} months, not {a.years:g} years.")
        print(f"    Hard cap on cost: {money(CEILING * POST_READ)}.")

    print(f"\n  spent on this estimate: {money(api.spend)}")
    print("  nothing else is pulled until you approve.\n")


if __name__ == "__main__":
    main()
