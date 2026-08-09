#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", os.getcwd()))
PLANS_DIR = PROJECT_ROOT / "knowledge" / "plans"
FIXTURES_DIR = PROJECT_ROOT / ".claude" / "tests" / "fixtures"
AUDIT_LOG = PROJECT_ROOT / ".claude" / "logs" / "sdlc-audit.log"

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


def get_plan_status(plan_path: Path) -> str | None:
    try:
        content = plan_path.read_text()
        match = re.search(r"^status:\s*(\S+)", content, re.MULTILINE)
        if match:
            return match.group(1).lower()
    except Exception:
        pass
    return None


def get_last_commit_info() -> tuple[str, str, list[str]]:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        msg = subprocess.check_output(
            ["git", "log", "-1", "--format=%s"],
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        files_out = subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"],
            cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
        )
        files = [f.strip() for f in files_out.splitlines() if f.strip()]
        return sha, msg, files
    except Exception:
        return "", "", []


def log_audit(entry: str) -> None:
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {entry}\n")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    command = data.get("tool_input", {}).get("command", "")

    if not re.search(r"\bgit\s+commit(?:\s|$)", command):
        sys.exit(0)

    sha, msg, files = get_last_commit_info()
    if not sha or not files:
        sys.exit(0)

    significant = [f for f in files if f in SIGNIFICANT_EXACT or any(f.lower().startswith(p) for p in SIGNIFICANT_PREFIXES)]
    if not significant:
        sys.exit(0)

    if "[skip-gate:" in msg:
        bypass_reason = re.search(r"\[skip-gate:\s*([^\]]+)\]", msg)
        reason = bypass_reason.group(1).strip() if bypass_reason else "unspecified"
        log_audit(f"BYPASS {sha} — {len(significant)} infra file(s) — reason: {reason} — files: {', '.join(significant)}")
        sys.exit(0)

    violations = []
    for rel_path in significant:
        fixture = resolve_fixture(rel_path)
        plan_name = resolve_plan_name(rel_path, fixture)

        if plan_name == "bootstrap-exempt":
            continue

        plan_path = PLANS_DIR / f"{plan_name}.md"
        fixture_exists = bool(fixture)

        missing = []
        if not plan_path.exists():
            missing.append(f"plan missing: knowledge/plans/{plan_name}.md")
        else:
            status = get_plan_status(plan_path)
            if status not in VALID_STATUSES:
                missing.append(f"plan status '{status}' not ready")
        if not fixture_exists:
            missing.append(f"fixture missing: .claude/tests/fixtures/{derive_feature_name(rel_path)}.json")

        if missing:
            violations.append((rel_path, missing))

    if not violations:
        log_audit(f"PASS {sha} — {len(significant)} infra file(s) verified — {', '.join(significant)}")
        sys.exit(0)

    for path, issues in violations:
        log_audit(f"VIOLATION {sha} — {path} — {'; '.join(issues)}")

    lines = [
        "",
        "SDLC POST-COMMIT AUDIT",
        f"  Commit {sha} landed infra files WITHOUT SDLC artifacts.",
        "  (Subagent commit or bash redirect bypassed the pre-gate.)",
        "",
    ]
    for path, issues in violations:
        lines.append(f"  File: {path}")
        for issue in issues:
            lines.append(f"    x {issue}")
    lines += [
        "",
        "  Fix now:",
        "    1. Create missing plan + fixture files",
        "    2. Commit them: git add <artifacts> && git commit",
        "  Or document the bypass:",
        "    git commit --amend -m '...[skip-gate: subagent-dispatch]'",
        f"  Audit log: .claude/logs/sdlc-audit.log",
    ]
    print("\n".join(lines), file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
