#!/usr/bin/env python3
"""
pii-brand-guard.py — PostToolUse(Write, Edit) hook  [canonical — claude-infra]

Fires after every Write or Edit. Scans written content for:
  1. Personal email addresses in content (brand/contact policy violation)
  2. PII (email, phone) in public-facing paths (healthcare/privacy violation)
  3. Hardcoded pricing in code files (operational-consistency violation)

Configuration: reads <project>/.claude/infra-config.json at runtime.
If no config found, uses safe empty defaults (warns but doesn't block).

infra-config.json schema:
{
  "pii_guard": {
    "personal_email_names": [],                        // names before @ to block — fill in yours
    "approved_email": "hello@example.co",            // exempt from PII scan
    "approved_phone": "98765 43210",                 // exempt from PII scan
    "high_risk_paths": ["app/", "components/"],      // PII scan triggers here
    "exempt_paths": ["OPERATIONAL_POLICIES"]         // skip these entirely
  }
}

Hook type: PostToolUse
Matcher: Write, Edit
Severity: non-blocking warn only
"""

import json
import os
import re
import sys
from pathlib import Path

# ── Load project config ───────────────────────────────────────────────────────

def load_config(cwd: str) -> dict:
    config_path = Path(cwd) / ".claude" / "infra-config.json"
    try:
        with open(config_path) as f:
            return json.load(f).get("pii_guard", {})
    except Exception:
        return {}


# ── PII patterns (universal) ─────────────────────────────────────────────────

PII_PATTERNS = [
    (re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'), "email address"),
    (re.compile(r'\b(?:\+91[\s\-]?)?[6-9]\d{9}\b'), "Indian phone number"),
    (re.compile(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}\b'), "Aadhaar-format number"),
]

CODE_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.py'}

DEFAULT_EXEMPT = [
    '/.env', '/.env.local', '/.env.example',
    '/contact', '/about', '/.claude/', '/tests/', '/test/',
    '.example.', 'README',
]


def build_personal_email_pattern(names: list[str]):
    if not names:
        return None
    escaped = [re.escape(n) for n in names]
    return re.compile(r'\b(' + '|'.join(escaped) + r')@\S+\b', re.IGNORECASE)


def is_exempt(path: str, extra_exempt: list[str]) -> bool:
    all_exempt = DEFAULT_EXEMPT + extra_exempt
    return any(seg in path for seg in all_exempt)


def is_high_risk(path: str, high_risk_paths: list[str]) -> bool:
    return any(seg in path for seg in high_risk_paths)


def is_code_file(path: str) -> bool:
    return Path(path).suffix in CODE_EXTENSIONS


def scan(content: str, file_path: str, cwd: str, cfg: dict) -> list[str]:
    warnings = []
    if not content:
        return warnings

    rel = os.path.relpath(file_path, cwd) if os.path.isabs(file_path) else file_path
    normalized = rel.replace(os.sep, '/')

    exempt_paths = cfg.get("exempt_paths", [])
    if is_exempt(normalized, exempt_paths):
        return warnings

    high_risk_paths = cfg.get("high_risk_paths", [])
    approved_email = cfg.get("approved_email", "")
    approved_phone = cfg.get("approved_phone", "").replace(" ", "")
    personal_names = cfg.get("personal_email_names", [])

    # 1. Personal email guard
    pattern = build_personal_email_pattern(personal_names)
    if pattern:
        found = pattern.findall(content)
        if found:
            names = list(set(found))
            warnings.append(
                f"PERSONAL EMAIL DETECTED: {[n+'@...' for n in names]} found in `{rel}`. "
                f"Only approved business contact details should appear in content."
            )

    # 2. PII in high-risk paths
    if high_risk_paths and is_high_risk(normalized, high_risk_paths):
        for pii_pattern, label in PII_PATTERNS:
            matches = pii_pattern.findall(content)
            if matches:
                filtered = [
                    m for m in matches
                    if approved_email not in str(m)
                    and approved_phone not in str(m).replace(" ", "")
                ]
                if filtered:
                    redacted = str(filtered[0])[:4] + "***"
                    warnings.append(
                        f"PII RISK: {label} in public-facing `{rel}` (e.g. `{redacted}`). "
                        f"Use server-only data fetching — never expose PII in rendered output."
                    )

    # 3. Hardcoded pricing in code files
    if is_code_file(normalized):
        pricing = re.search(r'₹\s*\d[\d,\s]*000', content)
        if pricing:
            warnings.append(
                f"HARDCODED PRICING in `{rel}`: use a constant or reference your cost/policy file."
            )

    return warnings


def main() -> None:
    try:
        raw = sys.stdin.read()
        hook_data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_input = hook_data.get("tool_input", {})
    cwd = hook_data.get("cwd", os.getcwd())
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not file_path or not content:
        sys.exit(0)

    cfg = load_config(cwd)
    warnings = scan(content, file_path, cwd, cfg)

    if not warnings:
        sys.exit(0)

    message = "CONTENT GUARD — issues in written content:\n\n" + "\n\n".join(
        f"• {w}" for w in warnings
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
