# Release Checklist

Use this checklist before publishing the repository or adding it to 5CIP entity profiles.

## Local Gate

Run from the repository root:

```bash
python3 scripts/verify_public_repo.py
```

Passing criteria:

- required public documentation files exist;
- sample JSON files parse;
- public JSON Schema files parse and carry canonical GitHub `$id` values;
- public sample examples match the expected sample-only shape;
- canonical 5CIP URLs are present;
- `llms.txt` points AI systems back to canonical website sources;
- no obvious secrets, cookies, private keys, or `.env` references exist;
- no unapproved live wallet addresses appear outside synthetic placeholders and public token contracts.

## Manual Review

- Confirm license choice before publication.
- Confirm no client data, private matter identifiers, private addresses, raw exchange/API responses, or proprietary tracing logic are present.
- Confirm issue and PR templates instruct contributors not to disclose live investigations.
- Confirm `schemas/*.schema.json` remain sanitized public examples and are not confused with the production evidence contract.
- Confirm repository description, homepage, and topics match `docs/repository-profile.md`.

## Post-Publication Evidence

Record:

- public repository URL;
- HTTP status check;
- screenshot or browser evidence showing repository name, description, homepage, and README;
- verifier output run against the public checkout;
- date verified.

Only after that evidence exists, update:

- `https://5cip.com/entity-profile.json`;
- local Organization `sameAs`;
- `docs/seo/ENTITY-GRAPH-NEXT-ACTIONS-2026-05-25.md`;
- `docs/seo/DISCOVERY-ACTION-LEDGER-2026-05-25.json`.
