# Evidence Schema

This document describes sanitized sample shapes for public documentation.

The production evidence packet includes PDF, JSON, CSV, WORM manifest, and signatures. This public schema is intentionally incomplete and does not expose proprietary internals.

Machine-readable public sample schemas:

- `../schemas/evidence-packet.schema.json`
- `../schemas/vasp-subpoena-packet.schema.json`

These schemas are for public documentation and CI verification only. They are not the production evidence contract and must not be expanded with client data, exchange API payloads, private keys, or live investigation artifacts.

## Transaction Evidence

```json
{
  "tx_hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
  "chain": "ethereum",
  "block_number": 12345678,
  "timestamp_utc": "2026-05-25T00:00:00Z",
  "from": "0x0000000000000000000000000000000000000000",
  "to": "0x1111111111111111111111111111111111111111",
  "asset": {
    "symbol": "USDT",
    "token_contract": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "raw_amount": "1000000",
    "decimal_amount": "1.000000"
  },
  "confidence_tier": "Tier 1A",
  "verification_sources": [
    "block_explorer",
    "internal_parser"
  ]
}
```

## Evidence Packet Manifest

```json
{
  "case_id": "CJ-PUBLIC-SAMPLE",
  "methodology_version": "public-v1",
  "created_at_utc": "2026-05-25T00:00:00Z",
  "files": [
    {
      "path": "01-summary/case-summary.pdf",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "content_type": "application/pdf"
    }
  ],
  "signature": {
    "type": "detached-gpg",
    "public_key_url": "https://5cip.com/5cip-gpg-public.asc"
  }
}
```

## VASP Packet Shape

```json
{
  "vasp": "example-exchange",
  "jurisdiction": "example",
  "request_type": "subpoena_or_disclosure_request",
  "transactions": [
    {
      "tx_hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
      "chain": "ethereum",
      "from": "0x0000000000000000000000000000000000000000",
      "to": "0x1111111111111111111111111111111111111111",
      "block_number": 12345678,
      "timestamp_utc": "2026-05-25T00:00:00Z",
      "amount_usd_at_block_time": "100.00",
      "confidence_tier": "Tier 1A"
    }
  ],
  "requested_records": [
    "customer_kyc",
    "deposit_address_owner",
    "withdrawal_history_for_bounded_date_range"
  ]
}
```
