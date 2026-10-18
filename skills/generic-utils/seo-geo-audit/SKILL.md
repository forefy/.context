---
name: seo-geo-audit
description: Turn a public-facing website into optimized for search engines and generative search engines by using all efficient means
---

Go over the source code and live site (ask the user) and optimize GEO and SEO according to obvious judgement, but don’t leave out any of these:

- Go to https://schema.org/docs/schemas.html and browse schemas we should use, as well as breadcrumbs, for rich results and JSON-LD content for search engines
- Drive a browser to https://www.seoptimer.com/ and run a free login-less site audit and apply all code adjustments to satisfy and get a top score.
- Use the Open Graph checker https://www.opengraph.xyz/ to ensure that when sites are sent over social media, Open Graph is optimized per page or important page we are sharing in-app.
- User might have a CDN like Cloudflare that does caching, or any other infrastructural service that we don’t want to conflict with; we can use the browser and ask the user to log in there too for tweaks.
- Run a generic security audit because stuff like immature security headers revealing technologies, stack traces, and console log errors may lower SEO
- Check for llms.txt - and concisely create one if missing.
- Ensure correctly generating sitemap.xml (with entries that won’t lower our score)
- Use a browser driver to go to https://search.google.com/ and ensure the site is listed on Google Search Console as an asset, the sitemap is submitted lately, and inspect any page issues and fix them.
- Adapt keywords per page for the content and highly optimize for specific search queries (best if you consult with the user on what you think is the right set)
- Ensure accessibility, privacy, terms, are applied to high extend (unless the user opts out of privacy/terms) to best results

# Limits to realize

- We don’t want to break anything or over-optimize, especially in non-significant, riskier areas.
- Always cross-check optimizations to see we aren’t breaking anything.
- Don’t stray into creating content or feature additions that might improve SEO if the user hadn’t asked for it- but you may very well suggest those.

# Verification
Your goal is only done after site with all fixes went to prod, we verified everything is healthy, and seoptimer, opengraph, google search and all the tools we used the browser to optimize are now close to perfect or as best as we can achieve without sacrificing app logic or user intents.
