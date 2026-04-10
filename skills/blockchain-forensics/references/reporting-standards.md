# Reporting and Evidence Standards

## 10.1 Evidence Hygiene
- Every claim must cite a tx hash, block number, or archived URL
- Never attribute based on a single OSINT signal
- Distinguish between confirmed facts and hypotheses in your report
- All wallet labels should state the basis for attribution (e.g., "tagged as Lazarus Group per OFAC SDN 2022-04-14")

## 10.2 Archiving Protocol
- Screenshot every Etherscan page, Telegram post, social media mention that supports your findings
- Use `web.archive.org/save/[URL]` to create permanent, timestamped archives
- Store archives in a dated folder structure: `YYYY-MM-DD_incident-name/screenshots/`
- Export Breadcrumbs or MetaSleuth graphs as PNG/PDF for the report appendix

## 10.3 Exchange and Law Enforcement Cooperation
- **Exchanges (Binance, OKX, Kraken, Coinbase):** Email their security/compliance teams with the attacker's deposit address, transaction hashes, and the theft evidence. Most have fast-track freeze processes for documented hacks.
- **Law enforcement:** FBI IC3 (ic3.gov), Interpol, national cybercrime units. Provide: victim details, full transaction log, fund flow diagram, current fund location.
- **Legal pathway required:** Confirm a recovery mechanism exists before investing major investigation effort. No legal pathway = monitoring only.

## 10.4 Public Disclosure Considerations
- Public disclosure can pressure exchanges to freeze funds faster
- But it can also alert the attacker to accelerate fund movement
- General rule: coordinate with affected protocol/exchange first; publish after freeze is in place or fails
- Follow ZachXBT's model: publish detailed evidence with wallet maps, timeline, and OSINT corroboration

## Report Structure

```
1. Executive Summary (1 paragraph: what happened, how much, where funds are)
2. Incident Timeline (chronological tx-by-tx sequence)
3. Fund Flow Analysis (diagram + table of all hops)
4. Attribution Evidence (transaction patterns + OSINT findings)
5. Current Fund Status (still on-chain / bridged / CEX / OTC)
6. Recovery Recommendations (exchange contact, law enforcement referral)
7. Appendix (all addresses, tx hashes, archived screenshots)
```
