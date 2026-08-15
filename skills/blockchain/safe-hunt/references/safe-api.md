# Safe Transaction Service API Reference

## Base URLs (per network)

```
ethereum  → https://api.safe.global/tx-service/eth/api/v1
polygon   → https://api.safe.global/tx-service/pol/api/v1
arbitrum  → https://api.safe.global/tx-service/arb1/api/v1
optimism  → https://api.safe.global/tx-service/oeth/api/v1
base      → https://api.safe.global/tx-service/base/api/v1
sepolia   → https://api.safe.global/tx-service/sep/api/v1
gnosis    → https://api.safe.global/tx-service/gno/api/v1
avalanche → https://api.safe.global/tx-service/avax/api/v1
bnb       → https://api.safe.global/tx-service/bnb/api/v1
```

All endpoints are **publicly readable, no auth required** for GET requests.
Safe addresses must be EIP-55 checksummed - use `eth_utils.to_checksum_address()` or equivalent.

---

## Key Endpoints

### Get Safe Config
```
GET {base}/safes/{address}/
```
Returns: `address`, `nonce`, `threshold`, `owners[]`, `masterCopy`, `modules[]`, `fallbackHandler`, `guard`, `moduleGuard`, `version`

**Critical fields for analysis:**
- `threshold` - number of required confirmations
- `owners` - list of owner addresses
- `guard` - `0x000...000` means no guard set
- `modules` - list of enabled module addresses (empty = good)
- `version` - e.g. `"1.3.0"`, `"1.4.0"`, `"1.1.1"`
- `masterCopy` - implementation address (cross-ref with known versions)
- `fallbackHandler` - should be standard CompatibilityFallbackHandler

Returns 404 if address is not a registered Safe.

---

### Get Transaction History
```
GET {base}/safes/{address}/multisig-transactions/?limit=50&ordering=-nonce
GET {base}/safes/{address}/multisig-transactions/?executed=false&ordering=-nonce   (pending only)
GET {base}/safes/{address}/multisig-transactions/?executed=true&ordering=-nonce    (executed only)
```

Each transaction object:
```json
{
  "safeTxHash": "0x...",
  "to": "0x...",
  "value": "0",
  "data": "0x...",
  "operation": 0,           // 0=CALL, 1=DELEGATECALL
  "gasToken": "0x000...000",
  "safeTxGas": 0,
  "baseGas": 0,
  "gasPrice": "0",
  "refundReceiver": "0x000...000",
  "nonce": 42,
  "isExecuted": true,
  "isSuccessful": true,
  "executor": "0x...",
  "confirmationsRequired": 3,
  "confirmations": [...],
  "dataDecoded": {
    "method": "addOwnerWithThreshold",
    "parameters": [
      {"name": "owner", "type": "address", "value": "0x..."},
      {"name": "_threshold", "type": "uint256", "value": "2"}
    ]
  }
}
```

**Key fields for analysis:**
- `operation` - `1` = delegatecall (needs scrutiny)
- `gasToken` - non-zero = custom gas token (suspicious)
- `refundReceiver` - non-zero-address = custom refund target
- `dataDecoded.method` - decoded function name
- `executor` - who submitted the tx on-chain
- `isExecuted` / `isSuccessful` - execution state

---

### Get All Safes Owned By Address
```
GET {base}/owners/{address}/safes/
```
Returns: `{ "safes": ["0x...", "0x..."] }`

Use to: expand a known team member's address into all Safes they participate in.

---

### Get All Safes Using a Module
```
GET {base}/modules/{moduleAddress}/safes/
```
Returns: `{ "safes": ["0x...", "0x..."] }`

Use to: find all Safes using a specific (potentially risky) module address.

---

### Get Safe Creation Info
```
GET {base}/safes/{address}/creation/
```
Returns: `created`, `creator`, `transactionHash`, `factoryAddress`, `masterCopy`, `setupData`

---

## Known Contract Addresses

### Trusted MultiSend (safe to delegatecall)
```
0x40A2aCCbd92BCA938b02010E17A5b8929b49130D  MultiSend 1.3.0
0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761  MultiSend 1.4.0
0x998739BFdAAdde7C933B942a68053933098f9EDa  MultiSendCallOnly 1.3.0
0x9641d764fc13c8B624c04430C7356C1C7C8102e2  MultiSendCallOnly 1.4.0
```

### Standard Fallback Handlers
```
0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4  CompatibilityFallbackHandler 1.3.0
0xfd0732Dc9E303f09fCEf3a7388Ad10A83459Ec99  CompatibilityFallbackHandler 1.4.0
```

### Known Safe Versions by masterCopy
```
0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552  → 1.3.0
0x41675C099F32341bf84BFc5382aF534df5C7461a → 1.4.0
0x6851D6fDFAfD08c0295C392436245E5bc78B0185 → 1.2.0  (outdated)
0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F → 1.1.1  (outdated)
0xaE32496491b53841efb51829d6f886387708F99B → 1.1.0  (outdated)
```

---

## Rate Limiting

- No hard published limit, but be respectful: add 0.2–0.5s delay between requests in sweeps
- Use `asyncio` with semaphore (max 10 concurrent) for sweep mode
- The sweep.py script handles this automatically

---

## Error Handling

| Status | Meaning |
|--------|---------|
| 200 | OK |
| 404 | Address is not a registered Safe (skip silently) |
| 422 | Invalid address format (not checksummed) |
| 429 | Rate limited - back off 5s and retry |
| 5xx | API error - retry once, then skip |
