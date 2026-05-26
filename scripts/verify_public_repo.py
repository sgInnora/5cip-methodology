#!/usr/bin/env python3
"""Pre-publication verifier for the 5CIP public methodology repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "LICENSE.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CITATION.cff",
    "llms.txt",
    "docs/ai-citation.md",
    "docs/confidence-tiers.md",
    "docs/evidence-schema.md",
    "docs/repository-profile.md",
    "docs/release-checklist.md",
    "schemas/evidence-packet.schema.json",
    "schemas/vasp-subpoena-packet.schema.json",
    "examples/sample-evidence-packet.json",
    "examples/vasp-subpoena-packet.sample.json",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/documentation.yml",
    ".github/pull_request_template.md",
    ".github/workflows/verify.yml",
]

REQUIRED_MARKERS = {
    "README.md": [
        "https://5cip.com/",
        "https://5cip.com/methodology",
        "https://5cip.com/entity-profile.json",
        "Do not infer recovery guarantees",
        "schemas/evidence-packet.schema.json",
        "See `LICENSE.md`",
    ],
    "LICENSE.md": [
        "Creative Commons Attribution 4.0",
        "MIT License",
        "not legal advice",
        "not a recovery guarantee",
    ],
    "docs/evidence-schema.md": [
        "../schemas/evidence-packet.schema.json",
        "../schemas/vasp-subpoena-packet.schema.json",
        "not the production evidence contract",
    ],
    "llms.txt": [
        "https://5cip.com/ai-citation-map.json",
        "profile URLs not listed in entity-profile.json",
    ],
    "docs/repository-profile.md": [
        "crypto-forensics",
        "https://github.com/5cip/5cip-methodology",
        "sameAs Gate",
        "LICENSE.md",
    ],
    "docs/release-checklist.md": [
        "Post-Publication Evidence",
        "entity-profile.json",
    ],
    "CITATION.cff": [
        "repository-code: \"https://github.com/5cip/5cip-methodology\"",
        "url: \"https://5cip.com/methodology\"",
    ],
}

SCHEMA_FILES = [
    "schemas/evidence-packet.schema.json",
    "schemas/vasp-subpoena-packet.schema.json",
]

SECRET_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY",
        r"\bapi[_-]?key\s*[:=]",
        r"\bsecret\s*[:=]",
        r"\bpassword\s*[:=]",
        r"\bauth[_-]?token\s*[:=]",
        r"\bcookie\s*[:=]",
    ]
]

ADDRESS_RE = re.compile(r"0x[a-fA-F0-9]{40}")
APPROVED_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x1111111111111111111111111111111111111111",
    "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "0x6b175474e89094c44da98b954eedeac495271d0f",
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def read(path: str, failures: list[str]) -> str:
    full_path = ROOT / path
    if not full_path.exists():
        fail(f"missing required file: {path}", failures)
        return ""
    return full_path.read_text(encoding="utf-8")


def check_required_files(failures: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not (ROOT / path).exists():
            fail(f"missing required file: {path}", failures)


def check_json_examples(failures: list[str]) -> None:
    for path in ["examples/sample-evidence-packet.json", "examples/vasp-subpoena-packet.sample.json"]:
        text = read(path, failures)
        if not text:
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON in {path}: {exc}", failures)
            continue
        if not data:
            fail(f"empty JSON example: {path}", failures)


def check_json_schemas(failures: list[str]) -> None:
    for path in SCHEMA_FILES:
        text = read(path, failures)
        if not text:
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON schema in {path}: {exc}", failures)
            continue
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"{path} missing draft 2020-12 $schema", failures)
        if not str(data.get("$id", "")).startswith("https://github.com/5cip/5cip-methodology/"):
            fail(f"{path} missing canonical GitHub $id", failures)
        if not data.get("title") or not data.get("required"):
            fail(f"{path} missing title or required fields", failures)


def check_sample_shapes(failures: list[str]) -> None:
    packet = read("examples/sample-evidence-packet.json", failures)
    subpoena = read("examples/vasp-subpoena-packet.sample.json", failures)
    if packet:
        data = json.loads(packet)
        if data.get("sample_only") is not True:
            fail("sample evidence packet must have sample_only=true", failures)
        if data.get("methodology_url") != "https://5cip.com/methodology":
            fail("sample evidence packet methodology_url mismatch", failures)
        if data.get("citation_map_url") != "https://5cip.com/ai-citation-map.json":
            fail("sample evidence packet citation_map_url mismatch", failures)
        for claim in data.get("claims", []):
            tier = claim.get("confidence_tier")
            if tier not in {"Tier 1A", "Tier 1B", "Tier 2", "Tier 3"}:
                fail(f"sample evidence packet invalid confidence tier: {tier}", failures)
            if not claim.get("evidence"):
                fail(f"sample evidence packet claim has no evidence: {claim.get('claim_id')}", failures)
    if subpoena:
        data = json.loads(subpoena)
        if data.get("sample_only") is not True:
            fail("VASP sample packet must have sample_only=true", failures)
        if data.get("canonical_guidance_url") != "https://5cip.com/topics/vasp-subpoena-checklist":
            fail("VASP sample packet canonical guidance URL mismatch", failures)
        for tx in data.get("transactions", []):
            if not re.fullmatch(r"0x[a-fA-F0-9]{64}", tx.get("tx_hash", "")):
                fail("VASP sample packet transaction has invalid tx_hash", failures)
            if tx.get("token_contract", "").lower() not in APPROVED_ADDRESSES:
                fail(f"VASP sample packet token contract not approved: {tx.get('token_contract')}", failures)


def check_markers(failures: list[str]) -> None:
    for path, markers in REQUIRED_MARKERS.items():
        text = read(path, failures)
        for marker in markers:
            if marker not in text:
                fail(f"{path} missing marker: {marker}", failures)


def check_sensitive_patterns(failures: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.name == ".env" or relative.endswith("/.env"):
            fail(f"forbidden env file present: {relative}", failures)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"sensitive marker in {relative}: {pattern.pattern}", failures)
        for address in ADDRESS_RE.findall(text):
            if address.lower() not in APPROVED_ADDRESSES:
                fail(f"unapproved wallet-like address in {relative}: {address}", failures)


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)
    check_json_examples(failures)
    check_json_schemas(failures)
    check_sample_shapes(failures)
    check_markers(failures)
    check_sensitive_patterns(failures)

    if failures:
        print("verify_public_repo: FAIL")
        for item in failures:
            print(f"  FAIL {item}")
        return 1

    print("verify_public_repo: PASS")
    print(f"root={ROOT}")
    print(f"requiredFiles={len(REQUIRED_FILES)}")
    print("jsonExamples=2")
    print(f"jsonSchemas={len(SCHEMA_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
