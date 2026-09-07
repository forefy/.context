# Disclosure-path signatures (Step 3)

Full signature table for the disclosure-path brute. Request each with GET (unless noted),
allow_redirects=False, verify=False, 10s timeout. A hit requires BOTH the status regex and the
body regex to match. Then: drop bodies containing `404 Not Found` or `This page can't be
displayed`; MD5-dedup bodies; and if EVERY signature matches, discard the whole host as a
catch-all responder.

| Occurrence name | Method | Path | Status | Body regex |
|---|---|---|---|---|
| package.json Disclosure | GET | `/package.json` | `2.*` | `.*` |
| jsconfig.json Disclosure | GET | `/jsconfig.json` | `2.*` | `.*` |
| Git Config 1 | GET | `/.git/config` | `2.*` | `\[core\]\|repositoryformatversion` |
| Git Config 2 | GET | `/.git/config~` | `2.*` | `\[core\]\|repositoryformatversion` |
| .git Disclosure | GET | `/.git` | `2.*` | `.*` |
| .svn Disclosure | GET | `/.svn` | `2.*` | `.*` |
| config.json Disclosure | GET | `/config.json` | `2.*` | `.*` |
| idx_config Directory Listing | GET | `/idx_config/` | `2.*` | `.*` |
| info.php Disclosure | GET | `/info.php` | `2.*` | `.*` |
| phpinfo Disclosure | GET | `/phpinfo.php` | `2.*` | `.*` |
| Jira File Read | GET | `/s/lkx/_/;/META-INF/maven/com.atlassian.jira/jira-webapp-dist/pom.properties` | `2.*` | `.*` |
| Eclipse Jetty Info Disclosure 1 (CVE-2021-28164) | GET | `/WEB-INF/web.xml` | `2.*` | `(?=.*<\/web-app>)(?=.*java.sun.com)` |
| Eclipse Jetty Info Disclosure 2 (CVE-2021-28164) | GET | `/%2e/WEB-INF/web.xml` | `2.*` | `(?=.*<\/web-app>)(?=.*java.sun.com)` |
| IIS Web Config | GET | `/web.config` | `2.*` | `.*` |
| Laravel App Log | GET | `/storage/logs/laravel.log` | `2.*` | `.*` |
| Zend App Init | GET | `/application/configs/application.ini` | `2.*` | `.*` |
| Wordpress debug.log | GET | `/wp-content/debug.log` | `2.*` | `.*` |
| Wordpress File Upload Plugin Logs | GET | `/wp-content/uploads/file-manager/log.txt` | `2.*` | `.*` |
| log.txt Disclosure | GET | `/log.txt` | `2.*` | `.*` |
| global.asa Disclosure | GET | `/global.asa` | `2.*` | `.*` |
| Pulse Secure | GET | `/dana-na/` | `2.*` | `by Pulse Secure, LLC` |
| Telerik UI (CVE-2019-18935 lineage) | GET | `/Telerik.Web.UI.WebResource.axd?type=rau` | `2.*` | `RadAsyncUpload handler is registered successfully` |
| Phinx Disclosure | GET | `/phinx.yml` | `2.*` | `.*` |
| Adminer SSRF | GET | `/adminer.php` | `2.*` | `.*` |
| Django in Debug Mode | GET | `/djgo` | `4.*` | `DEBUG =` |
| Git HEAD | GET | `/.git/HEAD` | `2.*` | `^ref: refs/` |
| Environment File Disclosure | GET | `/.env`, `/.env.local`, `/.env.production`, `/.env.backup` | `2.*` | `(?m)^(?:APP_KEY\|APP_SECRET\|DB_PASSWORD\|DATABASE_URL\|SECRET_KEY\|API_KEY\|AWS_SECRET_ACCESS_KEY\|PRIVATE_KEY)=.+` |
| npm Config Disclosure | GET | `/.npmrc` | `2.*` | `(?:_authToken\|_auth)\s*=\s*\S+` |
| Swagger / OpenAPI Disclosure *(info)* | GET | 10 paths, see note | `2.*` | `\"(?:swagger\|openapi)\"\s*:` |

Note the deliberately fingerprinted-by-body entries (Jetty web.xml, Telerik axd, Pulse, Django)
narrow to a real match; the `.*`-body entries fire on any 2xx, so the soft-404 filter, MD5 dedup,
and all-match catch-all discard are what keep them honest.

Swagger paths: `/swagger.json`, `/swagger/v1/swagger.json`, `/swagger/v2/swagger.json`, `/v2/api-docs`,
`/v3/api-docs`, `/openapi.json`, `/api-docs`, `/api/swagger.json`, `/api/v1/swagger.json`,
`/api/v2/swagger.json`. A hit is **informational** - it enumerates the API surface for later testing,
it is not itself a leak. Because the body regex requires a real `"swagger"`/`"openapi"` key, an SPA
catch-all serving `index.html` on every path cannot match it.

`.env.example` is deliberately **not** probed: it is published on purpose and its values are blank.
The `=.+` tail on the environment-file row enforces the same rule on the paths that are probed - a
`.env` served with empty values discloses variable names only and is not reported as a finding.

The `.git` rows now require real repo markers rather than any 2xx, so they no longer lean on the
soft-404 filter and md5 dedup to stay honest; `/.git/HEAD` is the cheapest single confirmation.
