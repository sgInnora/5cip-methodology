#!/usr/bin/env python3
"""Pre-publication verifier for the 5CIP public methodology repository."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
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
        "https://github.com/sgInnora/5cip-methodology",
        "- Owner: `sgInnora`",
        "sameAs Gate",
        "LICENSE.md",
    ],
    "SECURITY.md": [
        "5cip@innora.ai",
    ],
    "docs/release-checklist.md": [
        "Post-Publication Evidence",
        "entity-profile.json",
    ],
    "CITATION.cff": [
        "repository-code: \"https://github.com/sgInnora/5cip-methodology\"",
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
        if not str(data.get("$id", "")).startswith("https://github.com/sgInnora/5cip-methodology/"):
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
            if tier == "Tier 2":
                evidence = claim.get("evidence", [])
                if len(evidence) < 2 or not any(item.get("type") != "label" for item in evidence):
                    fail(f"sample evidence packet Tier 2 claim needs a second record besides a label: {claim.get('claim_id')}", failures)
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


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        names = [n for n in result.stdout.decode("utf-8", "surrogateescape").split("\0") if n]
        if names:
            return [ROOT / name for name in names if (ROOT / name).exists()]
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        skip = False
        for part in path.relative_to(ROOT).parts:
            if part.startswith(".") and part != ".github":
                skip = True
                break
            if part in {"__pycache__", "node_modules", "venv"}:
                skip = True
                break
        if not skip:
            files.append(path)
    return files


def check_sensitive_patterns(failures: list[str]) -> None:
    for path in tracked_files():
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


# Wording this repository must not use about 5CIP. Admissibility is decided by a court, per jurisdiction and
# per case; the public wording is "structured for counsel review". The public name is 5CIP. The repository
# lives under the sgInnora account; no other GitHub owner is to be named for it.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
ALLOWED_EMAILS = {"5cip@innora.ai"}

# SHA-256 of an earlier internal name (lower case, 11 letters). The name itself is not written in this file.
RETIRED_NAME_SHA256 = "a5813462451f4c898ee5b78069cf51ce047055486caed7dbe1f6928967caf2b5"
RETIRED_NAME_LENGTH = 11

FORBIDDEN_CLAIMS = [
    re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    for pattern in [
        r"court(?:[-\u2010-\u2015]|\s+)(?:grade|ready|admissible)",
        r"github\.com/(?!sginnora/)\S*5cip",
        r"(?<![a-z0-9-])5cip/5cip[-]methodology",
        r"owner:\s*`?5cip`?\s*$",
    ]
]


def contains_retired_name(text: str) -> bool:
    # Every window of 11 consecutive letters, with everything that is not a letter removed first, so the
    # name is found whatever its case and also when a hyphen, a space, a line break or other punctuation
    # splits it.
    letters = re.sub(r"[^a-z]", "", text.lower())
    seen: set[str] = set()
    for start in range(len(letters) - RETIRED_NAME_LENGTH + 1):
        window = letters[start : start + RETIRED_NAME_LENGTH]
        if window in seen:
            continue
        seen.add(window)
        if hashlib.sha256(window.encode("ascii")).hexdigest() == RETIRED_NAME_SHA256:
            return True
    return False


def check_forbidden_claims(failures: list[str]) -> None:
    for path in tracked_files():
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_CLAIMS:
            if pattern.search(text):
                fail(f"wording this repository must not use in {relative}: {pattern.pattern}", failures)
        for value in EMAIL_RE.findall(text):
            if value.lower() not in ALLOWED_EMAILS:
                fail(f"e-mail address not on the allow-list in {relative}: {value}", failures)
        if contains_retired_name(text):
            fail(f"an earlier internal name appears in {relative}", failures)


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)
    check_json_examples(failures)
    check_json_schemas(failures)
    check_sample_shapes(failures)
    check_markers(failures)
    check_sensitive_patterns(failures)
    check_forbidden_claims(failures)

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
