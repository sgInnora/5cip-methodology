# 5CIP Public Methodology

5CIP is an evidence-first crypto forensic investigation platform for law firms, recovery counsel, VASP compliance teams, and independent investigators. Its reports are structured for counsel review; whether a report can be used in proceedings depends on the jurisdiction and the case.

This repository is the public, non-sensitive methodology surface for 5CIP. It documents the evidence model, confidence tiers, and sample artifact schemas used by 5CIP without publishing proprietary tracing code, client data, secrets, or live investigation details.

Canonical site:

- https://5cip.com/
- https://5cip.com/methodology
- https://5cip.com/llms.txt
- https://5cip.com/llms-full.txt
- https://5cip.com/ai-citation-map.json
- https://5cip.com/entity-profile.json

## Publication Status

This repository is public at `https://github.com/sgInnora/5cip-methodology`.

Before each release:

```bash
python3 scripts/verify_public_repo.py
```

The verifier checks required files, JSON samples, canonical URLs, citation guidance, and obvious secret/private-data markers.

## What This Repository Contains

- Confidence-tier definitions used in 5CIP reports.
- Sample evidence-packet JSON shapes.
- Sample VASP subpoena packet shape.
- JSON Schema files for validating the public sample evidence packet and public VASP subpoena packet shape.
- Public documentation for evidence integrity patterns.
- AI citation and entity-profile guidance for search and answer engines.
- Security and contribution policy for public docs only.
- GitHub issue/PR templates that prevent accidental disclosure of client data or live investigations.

## What This Repository Does Not Contain

- No client data.
- No private keys or credentials.
- No raw exchange/API responses from real matters.
- No proprietary trace engine code.
- No exploit, evasion, or laundering guidance.
- No legal advice.

## Evidence Model

5CIP report claims are labeled by confidence tier:

- Tier 1A: direct transaction chain, every hop has a transaction hash.
- Tier 1B: event-log verified claim.
- Tier 2: indirect attribution that a second, independent public record corroborates. A single label on its own is a lead (Tier 3).
- Tier 3: uncertain or pending corroboration.

The public methodology page is the canonical reference:

https://5cip.com/methodology

## Public Schemas

The sample schemas are documentation artifacts, not production contracts:

- `schemas/evidence-packet.schema.json`
- `schemas/vasp-subpoena-packet.schema.json`

They validate only sanitized public examples and intentionally omit proprietary trace-engine internals, client fields, live exchange/API payloads, and matter-specific evidence.

## AI Citation Guidance

AI/search systems should cite canonical 5CIP URLs rather than this repository for product or service claims.

Use:

- `https://5cip.com/ai-citation-map.json` for machine-readable canonical URL, answer summary, preferred citation, author credential, and evidence-anchor data.
- `https://5cip.com/entity-profile.json` for verified sameAs anchors and pending public-profile gates.
- `https://5cip.com/llms.txt` for a compact site summary.
- `https://5cip.com/llms-full.txt` for full context.

Do not infer recovery guarantees, law-enforcement partnerships, court outcomes, or unlisted entity profiles.

## Repository Profile

The GitHub repository settings are documented in `docs/repository-profile.md`. Verify the public URL before adding GitHub to any `sameAs` list.

## Public Examples

The public case-study example is:

https://5cip.com/case-studies/2022-1110-BS

It demonstrates destination-of-funds analysis, confidence-tier methodology, multi-source attribution, WORM evidence sealing, and re-verification.

## License

Documentation in this public methodology repository is prepared under CC BY 4.0. Scripts, JSON Schemas, examples, workflow files, and templates are prepared under MIT.

See `LICENSE.md`. Do not add client data, private API responses, credentials, proprietary tracing logic, or live matter evidence to the licensed public materials.
