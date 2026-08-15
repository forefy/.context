# Cloud-storage endpoints, fail indications & name permutations (Step 1)

Full provider endpoints, fail indications, and region lists for the public-bucket brute, plus
the name-permutation wordlists and templates.

## Contents
- Provider endpoints and fail indications (AWS, GCS, DigitalOcean, Alibaba, Oracle, Vultr)
- Name permutation wordlists (suffix words, common company words)
- Permutation templates and variation-building rules

## Provider endpoints and fail indications

Substitute `{name}` (candidate bucket name) and `{region}`. Treat a response as "exists / public"
only if its body contains NONE of that endpoint's fail indications (and does not contain
`Burp Suite Professional`). Parse XML/JSON/text by Content-Type; 5s timeout.

### AWS S3
- `https://{name}.s3.amazonaws.com`
  fail: `AccessDenied`, `NoSuchBucket`, `IllegalLocationConstraintException`, `AllAccessDisabled`
- `https://{name}.s3-{region}.amazonaws.com`
  fail: `AccessDenied`, `NoSuchBucket`, `PermanentRedirect`, `IllegalLocationConstraintException`, `AllAccessDisabled`
  regions: us-east-2, us-east-1, us-west-1, us-west-2, af-south-1, ap-east-1, ap-south-2,
  ap-southeast-3, ap-southeast-4, ap-south-1, ap-northeast-3, ap-northeast-2, ap-southeast-1,
  ap-southeast-2, ap-northeast-1, ca-central-1, eu-central-1, eu-west-1, eu-west-2, eu-south-1,
  eu-west-3, eu-south-2, eu-north-1, eu-central-2, il-central-1, me-south-1, me-central-1,
  sa-east-1, us-gov-east-1, us-gov-west-1

### Google Cloud Storage
- `https://www.googleapis.com/storage/v1/b/{name}`
  fail: `The specified bucket does not exist`, `Anonymous caller does not have storage.buckets.get`
- `https://{name}.storage.googleapis.com/`
  fail: (none - treat any non-error body as a hit; inspect manually)

### DigitalOcean Spaces
- `https://{name}.{region}.digitaloceanspaces.com`
  fail: (none defined - inspect body)
  regions: nyc1, nyc3, ams3, sfo2, sfo3, sgp1, lon1, fra1, tor1, blr1, syd1

### Alibaba OSS
- `https://{name}.oss-{region}.aliyuncs.com`
  fail: (none defined - inspect body)
  regions: oss-cn-hangzhou, oss-cn-shanghai, oss-cn-nanjing, oss-cn-qingdao, oss-cn-beijing,
  oss-cn-zhangjiakou, oss-cn-huhehaote, oss-cn-wulanchabu, oss-cn-shenzhen, oss-cn-heyuan,
  oss-cn-guangzhou, oss-cn-chengdu, oss-cn-hongkong, oss-us-west-1, oss-us-east-1,
  oss-ap-northeast-1, oss-ap-northeast-2, oss-ap-southeast-1, oss-ap-southeast-2,
  oss-ap-southeast-3, oss-ap-southeast-5, oss-ap-southeast-6, oss-ap-southeast-7, oss-ap-south-1,
  oss-eu-central-1, oss-eu-west-1, oss-me-east-1

### Oracle Cloud Object Storage (S3-compat)
- `https://{name}.compat.objectstorage.{region}.oraclecloud.com`
  fail: `AnonymousUserSubject`
  regions: ap-sydney-1, ap-melbourne-1, sa-saopaulo-1, sa-vinhedo-1, ca-montreal-1, ca-toronto-1,
  sa-santiago-1, eu-paris-1, eu-marseille-1, eu-frankfurt-1, ap-hyderabad-1, ap-mumbai-1,
  il-jerusalem-1, eu-milan-1, ap-osaka-1, ap-tokyo-1, mx-queretaro-1, mx-monterrey-1,
  eu-amsterdam-1, me-jeddah-1, eu-jovanovac-1, ap-singapore-1, af-johannesburg-1, ap-seoul-1,
  ap-chuncheon-1, eu-madrid-1, eu-stockholm-1, eu-zurich-1, me-abudhabi-1, me-dubai-1

### Vultr Object Storage
- `https://{region}.vultrobjects.com/{name}`
  fail: `NoSuchBucket`
  regions: ams1, blr1, ewr1, sjc1, sgp1, del1

By default probe **one random region** per region-templated endpoint (keep volume sane against
third-party infra). Only iterate every region for a deliberate deep pass.

## Name permutation wordlists

### Suffix words (appended/prefixed via templates)
archive, artifacts, assets, backup, bin, bucket, data, dev, dev-data, dev_data, devops, files,
git, it, logs, media, mediauploads, onboarding, ops, proj, project, prod, prod-data, prod_data,
prod-files, prod_files, reports, scripts, stage, staging, static, storage, temp, terraform, tf,
tf-files, tf_files, terraformbinaries, test, tmp, user-files, user_files, uploads

### Common company words (used to split the root label into fragments/initials)
company, group, tech, solutions, international, services, world, global, ai, io, team, inc, ask,
digital, data, bits, bit, open, edu, educaiton, learning, auto, stack

### Permutation templates
- Base (always applied): `{name}`
- Non-domain (applied only to non-domain-looking single/two-part variations):
  `{name}_{word}`, `{word}-{name}`, `{word}_{name}`, `{name}{word}`, `{name}{second_name}`,
  `{name}{second_name}-{word}`, `{name}{second_name}_{word}`, `{name}-{second_name}-{word}`,
  `{name}_{second_name}_{word}`, `{name}{second_name}{word}`

Variation building: root label via `tldextract`; if it contains `-`, split into
`name`/`second_name` and add initials `name[0]+second_name[0]`; for each common word found inside
the root, add the root with that word removed and the initials of the two surrounding parts.
