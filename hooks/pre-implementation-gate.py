#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SIGNIFICANT_PREFIXES = [
    ".claude/agents/",
    ".claude/hooks/",
    ".claude/commands/",
    ".claude/scripts/",
    "scripts/",
]

SIGNIFICANT_EXACT = {
    ".claude/settings.json",
}

STRIP_SUFFIXES = ["-hook", "-agent", "-guard", "-check", "-script"]

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", os.getcwd()))
PLANS_DIR = PROJECT_ROOT / "knowledge" / "plans"
EXTERNAL_PLANS_DIR = Path.home() / ".claude" / "plans"
FIXTURES_DIR = PROJECT_ROOT / ".claude" / "tests" / "fixtures"
AUDIT_LOG = PROJECT_ROOT / ".claude" / "logs" / "sdlc-audit.log"

FIXTURE_EXEMPT_EXACT = {".claude/settings.json"}

VALID_STATUSES = {"wiring", "evaluation", "done"}


def derive_feature_name(rel_path: str) -> str:
    name = Path(rel_path).stem
    for suffix in STRIP_SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name


def resolve_fixture(rel_path: str) -> dict:
    for candidate in [Path(rel_path).stem, derive_feature_name(rel_path)]:
        fixture_path = FIXTURES_DIR / f"{candidate}.json"
        if fixture_path.exists():
            try:
                return json.loads(fixture_path.read_text())
            except Exception:
                pass
    return {}


def resolve_plan_name(rel_path: str, fixture: dict) -> str:
    if fixture.get("plan"):
        return fixture["plan"]
    if fixture.get("feature"):
        return fixture["feature"]
    return derive_feature_name(rel_path)


def log_audit(entry: str) -> None:
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a") as f:
            from datetime import datetime
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {entry}\n")
    except Exception:
        pass


def get_staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        return []
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def get_plan_status(plan_path: Path) -> str | None:
    try:
        content = plan_path.read_text()
        match = re.search(r"^status:\s*(\S+)", content, re.MULTILINE)
        if match:
            return match.group(1).lower()
    except Exception:
        pass
    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    command = data.get("tool_input", {}).get("command", "")

    if not re.search(r"\bgit\s+commit(?:\s|$)", command):
        sys.exit(0)

    if "[skip-gate:" in command:
        print("SDLC gate: bypass token found — skipping checks.", file=sys.stderr)
        sys.exit(0)

    if os.environ.get("SKIP_IMPL_GATE") == "1":
        staged = get_staged_files()
        sig = [f for f in staged if f in SIGNIFICANT_EXACT or any(f.lower().startswith(p) for p in SIGNIFICANT_PREFIXES)]
        log_audit(f"BYPASS env-var — SKIP_IMPL_GATE=1 — staged: {', '.join(sig) if sig else 'none'}")
        print("SDLC gate: SKIP_IMPL_GATE=1 — skipping checks (logged).", file=sys.stderr)
        sys.exit(0)

    try:
        staged = get_staged_files()
    except Exception as e:
        print(f"SDLC gate: could not read staged files ({e}) — failing open.", file=sys.stderr)
        sys.exit(1)

    significant = [f for f in staged if f in SIGNIFICANT_EXACT or any(f.lower().startswith(p) for p in SIGNIFICANT_PREFIXES)]

    if not significant:
        sys.exit(0)

    blocked = []

    for rel_path in significant:
        fixture = resolve_fixture(rel_path)
        plan_name = resolve_plan_name(rel_path, fixture)

        if plan_name == "bootstrap-exempt":
            continue

        plan_path = PLANS_DIR / f"{plan_name}.md"
        external_plan_path = EXTERNAL_PLANS_DIR / f"{plan_name}.md"
        fixture_exists = bool(fixture)

        missing = []

        if plan_path.exists():
            status = get_plan_status(plan_path)
            if status is None:
                missing.append(f"plan has no 'status:' field: knowledge/plans/{plan_name}.md")
            elif status not in VALID_STATUSES:
                missing.append(
                    f"plan status '{status}' not ready (need: wiring|evaluation|done): knowledge/plans/{plan_name}.md"
                )
        elif external_plan_path.exists():
            pass
        else:
            missing.append(f"plan missing: knowledge/plans/{plan_name}.md (also checked ~/.claude/plans/)")

        fixture_required = rel_path not in FIXTURE_EXEMPT_EXACT
        if fixture_required and not fixture_exists:
            missing.append(f"fixture missing: .claude/tests/fixtures/{derive_feature_name(rel_path)}.json")
        elif fixture_exists:
            if fixture.get("type") == "test" and not fixture.get("test_cases"):
                missing.append(
                    f"fixture claims type:test but has no test_cases: .claude/tests/fixtures/{derive_feature_name(rel_path)}.json"
                )

        if missing:
            blocked.append((rel_path, missing))

    if blocked:
        lines = ["", "SDLC GATE BLOCKED"]
        for path, issues in blocked:
            lines.append(f"  File: {path}")
            for issue in issues:
                lines.append(f"    x {issue}")
        lines.append("")
        lines.append("  Fix: create missing artifacts, then retry commit.")
        lines.append("  Emergency bypass: include [skip-gate: reason] in commit message.")
        print("\n".join(lines), file=sys.stderr)
        sys.exit(2)

    log_audit(f"PASS pre-gate — {len(significant)} infra file(s) verified — {', '.join(significant)}")
    print(f"SDLC verified ({len(significant)} significant file(s) checked)", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
