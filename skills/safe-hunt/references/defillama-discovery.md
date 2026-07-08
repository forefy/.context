# DeFiLlama Discovery Reference

## Overview

DeFiLlama maintains treasury adapters for ~292 protocols in the DefiLlama-Adapters GitHub repo.
Each adapter JS file contains the protocol's treasury/governance Safe addresses in `owners:` arrays.

---

## GitHub URL Pattern

```
https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/treasury/{slug}.js
```

Where `{slug}` is the `treasury` field value from the DeFiLlama protocols API (without `.js` extension if it already has it).

### Get all protocol treasury slugs
```bash
curl -sL "https://api.llama.fi/protocols" | python3 -c "
import json, sys
data = json.load(sys.stdin)
slugs = [(p['name'], p['treasury']) for p in data if p.get('treasury')]
for name, slug in slugs:
    print(f'{name}\t{slug}')
"
```

---

## Address Extraction

Treasury adapter files follow several patterns. Extract ALL Ethereum addresses (`0x[0-9a-fA-F]{40}`) from the file, then validate each against the Safe API.

### Pattern 1: Named constant + owners array (most common)
```js
const LidoTreasury = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c";
module.exports = treasuryExports({
  ethereum: {
    owners: [LidoTreasury],
  }
})
```

### Pattern 2: Direct address in owners array
```js
module.exports = treasuryExports({
  ethereum: {
    owners: ["0xb8e1f3b966af4Ca02F0A4c95F4e4C55Bd2E8e63"],
  }
})
```

### Pattern 3: Multiple networks
```js
module.exports = treasuryExports({
  ethereum: { owners: ["0xABC..."] },
  polygon:  { owners: ["0xDEF..."] },
  arbitrum: { owners: ["0x123..."] },
})
```

### Pattern 4: Mixed owners and tokens (ignore token addresses)
```js
// tokens[] → contract addresses, NOT Safes - but still try against Safe API
// owners[] → likely Safe addresses
// The Safe API returns 404 for non-Safes, so safe to try all
```

---

## Extraction Script (inline)

```python
import re
import requests

ETH_ADDR_RE = re.compile(r'0x[0-9a-fA-F]{40}')
ZERO_ADDR = "0x0000000000000000000000000000000000000000"

def extract_addresses_from_adapter(slug):
    url = f"https://raw.githubusercontent.com/DefiLlama/DefiLlama-Adapters/main/projects/treasury/{slug}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return []
    addresses = list(set(ETH_ADDR_RE.findall(r.text)))
    # Filter out zero address and known non-Safe addresses (factory, etc.)
    return [a for a in addresses if a.lower() != ZERO_ADDR.lower()]

def get_all_treasury_slugs():
    r = requests.get("https://api.llama.fi/protocols", timeout=30)
    data = r.json()
    return [(p['name'], p['treasury']) for p in data if p.get('treasury')]
```

---

## Network Mapping

DeFiLlama uses these network keys in treasury adapters - map to Safe API network slugs:

| DeFiLlama key | Safe API slug |
|---------------|---------------|
| `ethereum` | `ethereum` |
| `polygon` | `polygon` |
| `arbitrum` | `arbitrum` |
| `optimism` | `optimism` |
| `base` | `base` |
| `bsc` / `binance` | `bnb` |
| `gnosis` / `xdai` | `gnosis` |
| `avalanche` | `avalanche` |

When an adapter lists addresses for multiple networks, check each address against the corresponding Safe API network.

---

## Protocol-Specific Lookup

For Mode 2 (single protocol), fuzzy-match the user's input against DeFiLlama protocol names:

```python
def find_protocol(name_query, protocols):
    name_lower = name_query.lower()
    # Exact match first
    exact = [p for p in protocols if p['name'].lower() == name_lower]
    if exact:
        return exact[0]
    # Partial match
    partial = [p for p in protocols if name_lower in p['name'].lower()]
    return partial[0] if len(partial) == 1 else partial  # return list if ambiguous
```

If ambiguous → ask user to clarify from the list.

---

## Expected Hit Rate

From testing:
- ~292 protocols have treasury adapters
- Each adapter typically contains 1–5 Safe addresses
- ~60–80% of `owners:` addresses are actual Safes (Safe API returns 200)
- ~20–40% are EOAs or token contracts (Safe API returns 404 - skip silently)
- Expect ~400–700 valid Safes from a full sweep

---

## Supplemental Discovery (when DeFiLlama misses a protocol)

If a protocol isn't in DeFiLlama:
1. **GitHub search**: `{protocol} multisig site:github.com` - look for deployed addresses in README or docs
2. **Etherscan labels**: `https://etherscan.io/accounts/label/safe` - labeled Safe accounts
3. **From known team member**: `GET /api/v1/owners/{known_team_address}/safes/`
4. **From known module**: `GET /api/v1/modules/{moduleAddress}/safes/` - if you know a module they use
