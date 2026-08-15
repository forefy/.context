---
name: cloud-bucket-brute
description: Active enumeration of publicly readable cloud-storage buckets - permutes a company name into candidate bucket names and probes AWS S3, Google Cloud, DigitalOcean, Alibaba, Oracle, and Vultr for anonymously accessible buckets. Use to find exposed or misconfigured cloud storage or leaked S3/GCS buckets for an authorized target.
---

## Contents
- Scope & authorization
- Name permutation scheme
- Probe logic
- Runnable snippets
- Output
- Reference file: `references/cloud-storage-endpoints.md`

## Scope & authorization

Run only against organizations you own or are contractually engaged to test. This is an **aggressive-3rdparty** check: it does not touch the target's own infrastructure, but it fires a high volume of requests at third-party cloud providers (AWS/GCP/DigitalOcean/Alibaba/Oracle/Vultr) about the target. Expect provider-side rate-limiting and logging. Keep the candidate list scoped to the org actually in scope.

Input is the set of the target's domains. Output is any bucket name that resolves to an anonymously reachable object store.

## Name permutation scheme

Turn each in-scope domain into candidate bucket names (this is the valuable part - carry it exactly):
1. Reduce the domain to its registrable root label (`tldextract(...).domain`, e.g. `foo-bar.co.uk` -> `foo-bar`) and seed the variation set with the raw name.
2. If the root contains `-`, split into `name` + `second_name`, and also add the **initials** `name[0]+second_name[0]`.
3. For each "common company word" that appears inside the root (`company, group, tech, solutions, international, services, world, global, ai, io, team, inc, ask, digital, data, bits, bit, open, edu, educaiton, learning, auto, stack`), add the name with that word **stripped out**, plus the **initials** of the two parts around it. (So `bugcrowd` yields `bugcrowd`, `bug`/`crowd` fragments, `bc`, etc.)
4. Expand every variation through the permutation templates against the suffix wordlist. Bare `{name}` is always tried; multi-word templates (`{name}_{word}`, `{word}-{name}`, `{word}_{name}`, `{name}{word}`, `{name}{second_name}`, `{name}{second_name}-{word}`, `{name}{second_name}_{word}`, `{name}-{second_name}-{word}`, `{name}_{second_name}_{word}`, `{name}{second_name}{word}`) are only applied to non-domain-looking single/two-part variations.

The full provider endpoint templates, per-provider **fail indications**, region lists, the 40-word suffix list, and the permutation templates are in `references/cloud-storage-endpoints.md`.

## Probe logic

For each candidate: GET the endpoint (5s timeout). Parse the body as XML/JSON/text by `Content-Type`. By default pick **one random region** per region-templated endpoint (set an "iterate all regions" flag only for a deep, much slower pass). Discard any response containing that provider's fail indications (e.g. AWS `AccessDenied`, `NoSuchBucket`, `IllegalLocationConstraintException`, `AllAccessDisabled`, `PermanentRedirect`; GCP `The specified bucket does not exist` / `Anonymous caller does not have storage.buckets.get`; Oracle `AnonymousUserSubject`; Vultr/DO `NoSuchBucket`), and discard any body containing `Burp Suite Professional` (interception artifact).

**Report a finding when**: an endpoint returns a body with **none** of its fail indications - the bucket exists and is anonymously reachable. Severity: Information Disclosure (verify listability/read of objects before rating impact).

## Runnable snippets

```bash
# single candidate, AWS virtual-host + GCP JSON API
NAME=acme-backups
curl -s "https://$NAME.s3.amazonaws.com" | grep -qiE 'AccessDenied|NoSuchBucket|IllegalLocationConstraint|AllAccessDisabled' \
  && echo "aws: not public" || echo "aws: PUBLIC/exists -> https://$NAME.s3.amazonaws.com"
curl -s "https://www.googleapis.com/storage/v1/b/$NAME" | grep -qiE 'does not exist|does not have storage.buckets.get' \
  && echo "gcp: not public" || echo "gcp: PUBLIC/exists"
```

```bash
# generate candidate names (permutation scheme) for a domain
python3 - <<'PY'
import tldextract
words=["archive","artifacts","assets","backup","bin","bucket","data","dev","dev-data","dev_data","devops","files","git","it","logs","media","mediauploads","onboarding","ops","proj","project","prod","prod-data","prod_data","prod-files","prod_files","reports","scripts","stage","staging","static","storage","temp","terraform","tf","tf-files","tf_files","terraformbinaries","test","tmp","user-files","user_files","uploads"]
common={"company","group","tech","solutions","international","services","world","global","ai","io","team","inc","ask","digital","data","bits","bit","open","edu","educaiton","learning","auto","stack"}
name=tldextract.extract("acme-corp.com").domain
variations=[(name,)]
if "-" in name:
    a,b=name.split("-",1); variations+=[(a,b),(a[0]+b[0],)]
for w in common:
    if w in name:
        variations+=[(name.replace(w,""),)]
tmpl_base=["{name}"]
tmpl_multi=["{name}_{word}","{word}-{name}","{word}_{name}","{name}{word}","{name}{second_name}","{name}{second_name}-{word}","{name}{second_name}_{word}","{name}-{second_name}-{word}","{name}_{second_name}_{word}","{name}{second_name}{word}"]
out=[]
for v in variations:
    tmpls=tmpl_base+(tmpl_multi if len(v)<=2 else [])
    for w in words:
        for t in tmpls:
            if "{second_name}" in t and len(v)!=2: continue
            s=t.replace("{name}",v[0]).replace("{word}",w)
            if len(v)==2: s=s.replace("{second_name}",v[1])
            if s not in out: out.append(s)
print("\n".join(out))
PY
```

## Output

Finish with a `candidate / provider / reachable?` ledger (or just the confirmed hits when the candidate list is large), then a verdict:
- **Clean** - candidates generated and probed across all six providers, nothing anonymously reachable.
- **Exposed** - list each public bucket URL, its provider, and whether objects are listable/readable. Fix: make buckets private, require authentication, and audit bucket-policy/ACL for anonymous grants.

Report whether the sweep was rate-limited or partial (e.g. one-region-only), so an incomplete run is not reported as clean.
