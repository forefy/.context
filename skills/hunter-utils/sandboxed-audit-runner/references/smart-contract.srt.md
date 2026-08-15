Sandbox profile for EVM smart contract audits. Allows GitHub dependency fetches, block explorer APIs, free public RPCs for fork testing, and package registries. All sensitive host credential paths are denied.

Copy the JSON block below to `.srt-audit.json` in the project root before starting the sandboxed session.

```json
{
  "network": {
    "allowedDomains": [
      "github.com",
      "raw.githubusercontent.com",
      "api.github.com",
      "registry.npmjs.org",
      "pypi.org",
      "files.pythonhosted.org",
      "crates.io",
      "static.crates.io",
      "api.etherscan.io",
      "api-goerli.etherscan.io",
      "api-sepolia.etherscan.io",
      "api.basescan.org",
      "api-optimistic.etherscan.io",
      "api.arbiscan.io",
      "mainnet.infura.io",
      "rpc.ankr.com",
      "cloudflare-eth.com",
      "eth.llamarpc.com",
      "base.llamarpc.com",
      "arb1.arbitrum.io"
    ],
    "deniedDomains": []
  },
  "filesystem": {
    "denyRead": [
      "~/.ssh",
      "~/.gnupg",
      "~/.aws",
      "~/.config/gcloud",
      "~/.npmrc",
      "~/.pypirc",
      "~/.netrc"
    ],
    "allowRead": [
      ".",
      "~/.foundry",
      "~/.cargo"
    ],
    "allowWrite": [
      ".",
      "/tmp",
      "~/.foundry/cache"
    ],
    "denyWrite": [
      ".env",
      ".env.*",
      "*.pem",
      "*.key"
    ]
  }
}
```
