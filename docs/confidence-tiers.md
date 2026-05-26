# Confidence Tiers

5CIP uses explicit confidence tiers so courts, counsel, and AI/search systems can distinguish direct evidence from inference.

## Tier 1A: Direct Chain

Use when every hop is directly supported by a transaction hash.

Required fields:

- source address;
- destination address;
- transaction hash;
- block number;
- UTC timestamp;
- token contract, if not native asset;
- raw amount and decimal amount;
- source of verification.

## Tier 1B: Event Log Verified

Use when the claim is supported by event logs but not necessarily by a full direct custody chain.

Examples:

- ERC-20 `Transfer` event;
- bridge event logs;
- smart-contract event proving deposit or withdrawal.

## Tier 2: Indirect Attribution

Use for evidence-supported inference.

Examples:

- timing correlation;
- bridge source/destination matching from one or more indexers;
- VASP or label-provider corroboration;
- address reuse;
- relayer funding pattern.

Tier 2 claims must identify the corroborating sources and limitations.

## Tier 3: Needs Corroboration

Use when the claim is plausible but not ready for legal reliance.

Tier 3 claims should not be presented as conclusions. They should be framed as leads for further investigation.

## Anti-Hallucination Rule

Never derive wallet addresses, amounts, or attribution from memory. Use current API outputs, public chain data, or verified report artifacts.
