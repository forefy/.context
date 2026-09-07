# Secret / API-token regexes (class 3)

Run every pattern over each captured response body. A match is a lead ("Hardcoded Secrets" insight), not a confirmed leak - verify the value is a real, private credential (some browser-side keys are intentionally public). De-duplicate matches per target; truncate the joined match string to 400 chars. (Illustrative example values were removed so the table ships no scannable tokens.)

| Name | Regex |
| --- | --- |
| Generic password | `\", ?\"Password\": ?\"[a-zA-Z].{4,32}?\"` |
| Fullstory API token | `na1\.by0x[a-zA-Z0-9]{84,100}\/[A-Z0-9]{7}` |
| Okta API token | `['\" ]00[a-zA-Z0-9\-\_]{40}['\" ]` |
| Segment API token | `sgp_[a-zA-Z0-9]{64}` |
| DigitalOcean user access token | `do(p\|o)_v1_[a-f0-9]{64}` |
| HuggingFace user access token | `hf_[a-zA-Z]{34}` |
| Grafana Cloud API token | `glc_ey([a-zA-Z0-9_-]{90})` |
| Adobe OAuth client secret | `(?i)\b(p8e-[a-z0-9-]{32})(?:[^a-z0-9-]\|$)` |
| ChatGPT / OpenAI API key | `sk-(?=[^\d]*\d)(?=[^\w]*[a-zA-Z])[\w\d]{48}` |
| Homebrew artifactory API token | `(?:\s\|=\|:\|"\|^)AKC[a-zA-Z0-9]{10,}` |
| Slack app token | `xox[baprso]-[0-9a-zA-Z]{10,48}(?:-[0-9a-zA-Z]{10,48})?` |
| GitHub access token (Classic) | `gh(o\|p\|u)_[a-zA-Z0-9]{36}` |
| GitHub access token (Fine-grained) | `github_pat_[0-9a-zA-Z_]{82}` |
| GitHub URI (creds in URL) | `git\+https:\/\/\w+:\w+@github\.com\/\w+\/\w+(-\w+)*\.git` |
| AWS S3 bucket | `(?:[A-Za-z0-9.-]{3,63}\.s3\.(?:amazonaws\.com\|customdomain\.com)\|s3(?:-global)?\.amazonaws\.com/[A-Za-z0-9.-]{3,63}\|[A-Za-z0-9.-]{3,63}\.s3\.[A-Za-z0-9-]+\.amazonaws\.com)(?:/.+?(?= \|\,\|\"\|\?))` |
| Firebase URL | `https?://(?=.{1,255}$)[0-9A-Za-z](?:(?:[0-9A-Za-z]\|-){0,61}[0-9A-Za-z])\.firebaseio\.com` |
| Slack Token | `(xox[p\|b\|o\|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32})` |
| Amazon AWS Access Key ID | `(?!.*EXAMPLE)AKIA[0-9A-Z]{16}` |
| Amazon MWS Auth Token | `amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` |
| Facebook Access Token | `EAACEdEose0cBA[0-9A-Za-z]+` |
| Google API Key | `AIza[0-9A-Za-z\\-_]{35}` |
| Google Cloud Platform OAuth | `[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com` |
| Google (GCP) service-account | `\"type\": \"service_account\"` |
| Google OAuth Access Token | `ya29\\.[0-9A-Za-z\\-_]+` |
| Heroku API Key | `(?i)heroku.*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}` |
| MailChimp API Key | `[0-9a-f]{32}-us[0-9]{1,2}` |
| Mailgun API Key | `key-[0-9a-zA-Z]{32}` |
| PayPal Braintree Access Token | `access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}` |
| Picatic API Key | `sk_live_[0-9a-z]{32}` |
| Slack Webhook | `https://hooks.slack.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}` |
| Stripe API Key | `(s\|r)k_(live\|test)_[0-9a-zA-Z]{24,255}` |
| Square Access Token | `sq0atp-[0-9A-Za-z\\-_]{22}` |
| Square OAuth Secret | `sq0csp-[0-9A-Za-z\\-_]{43}` |
| Telegram Bot Token | `bot\d{6}:[A-Za-z0-9_-]{34}` |
| MongoDB connection URI (creds) | `mongodb(?:\+srv)?://[^:@\s"']{1,64}:[^@\s"']{1,128}@[^"'\s]{4,256}` |
| Redis connection URI (creds) | `rediss?://:[^@\s"']{4,128}@[^"'\s]{4,256}` |
| PostgreSQL connection URI (creds) | `postgres(?:ql)?://[^:@\s"']{1,64}:[^@\s"']{4,128}@[^"'\s]{4,256}` |
| MySQL connection URI (creds) | `mysql2?://[^:@\s"']{1,64}:[^@\s"']{4,128}@[^"'\s]{4,256}` |
| MSSQL connection URI (creds) | `(?:mssql\|sqlserver)://[^:@\s"']{1,64}:[^@\s"']{4,128}@[^"'\s]{4,256}` |
| Bitbucket app password in URL | `https?://[^:@\s]+:[^@\s]+@bitbucket\.org` |
| Generic connection string | `[A-Z][A-Za-z]{1,32}=[^;]{1,64};[A-Z][A-Za-z]{1,32}=[^;]{1,64};[A-Z][A-Za-z]{1,32}=[^;]{1,64}` |
| OpenAI project key | `sk-proj-[A-Za-z0-9_-]{80,}` |
| OpenAI service-account key | `sk-svcacct-[A-Za-z0-9_-]{80,}` |
| Anthropic API key | `sk-ant-api\d{2}-[A-Za-z0-9_-]{93}` |
| npm access token | `npm_[A-Za-z0-9]{36}` |
| GitHub server-to-server token | `ghs_[0-9a-zA-Z]{36}` |
| GitHub refresh token | `ghr_[0-9a-zA-Z]{76}` |
| Discord bot token | `\b[MNO][A-Za-z0-9_-]{23,25}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,38}\b` |
| Discord webhook | `https?://discord(?:app)?\.com/api/webhooks/[0-9]{17,20}/[A-Za-z0-9_-]{60,80}` |
| GCP service-account private key id | `\"private_key_id\"\s*:\s*\"[0-9a-f]{40}\"` |
| Azure Blob URL *(identifier)* | `https?://[a-z0-9]{3,24}\.blob\.core\.windows\.net/[^\"'<>\s]{1,256}` |
| GCS bucket URL *(identifier)* | `https?://(?:storage\.googleapis\.com/[a-z0-9_.-]{3,63}\|[a-z0-9_.-]{3,63}\.storage\.googleapis\.com)` |
| Firebase Storage URL *(identifier)* | `https?://firebasestorage\.googleapis\.com/v0/b/[a-z0-9-]+\.appspot\.com` |
| AWS entity ID *(identifier)* | `\b(?:ASIA\|AROA\|AIDA\|AGPA\|AIPA\|ANPA\|ANVA\|APKA\|ACCA\|ASCA)[A-Z0-9]{16}\b` |


Notes: the original set also duplicated the `AIza...` Google-key pattern under several product labels (GCP API Key, Drive, Gmail) and the `...apps.googleusercontent.com` OAuth pattern under Drive/Gmail - they are the same two regexes, listed once here. When loading into `rules.txt` for the sweep snippet, prefix these names with a non-`ERR:` tag so they are never skipped on JS bundles.
## False-positive gates

Regex alone is not enough for the loose rows. Apply these before reporting:

- **Credential-keyword gate** (Generic connection string) - the `K=V;K=V;K=V` shape also describes inline CSS, cookie strings and i18n blobs, so keep the match only if the surrounding string carries a credential key: `(?i)\b(?:password|pwd|accountkey|sharedaccesssignature|apikey|secret|token|uid|user id)\s*=\s*[^;\s]{6,}`. Do **not** substitute an entropy floor here - it ranks backwards on this row (a real ODBC string measures ~4.0 bits/char, a CSS false positive ~4.04).
- **Repetition gate** - for the remaining unanchored rows (Generic password, Okta `00...{40}`, Homebrew `AKC...`, MailChimp `[0-9a-f]{32}-us[0-9]`), drop padded or repeated matches - Shannon entropy below **3.0 bits/char**, or a single character making up more than half the match. This catches `000...`/`xxxx...` placeholders and little else; it is a floor, not a classifier. Prefix-anchored keys (`sk-ant-`, `npm_`, `ghs_`, `AKIA`) need no gate at all - the prefix carries the specificity.
- **Placeholder / local gate** - for the connection URIs, drop the match when the host is `localhost`, `127.0.0.1`, `0.0.0.0`, an `example.*` domain, or a bare compose service name (`db`, `postgres`, `mongo`, `redis`), or when the password is a placeholder (`password`, `pass`, `secret`, `changeme`, `xxx`, `<...>`, `${...}`). Bundled docs and `.env.example` strings are the whole of the noise here; without this gate the five URI rows are net-negative.
- **Identifiers are not secrets** - rows tagged *(identifier)*, plus the AWS S3 bucket and Firebase URL rows, are public by design. Report them as an insight **with the next step attached** (list the bucket / check the ACL; append `/.json` to a Firebase RTDB URL to test the rule set), never as a leaked credential.
- **Discord snowflake gate** - the bot-token regex matches any three base64url segments of the right lengths, which minified bundles produce by accident. Base64url-decode segment 1 and keep the match only if it decodes to 17-20 ASCII digits.
