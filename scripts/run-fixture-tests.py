#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("GITHUB_WORKSPACE", "")) or Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / ".claude" / "tests" / "fixtures"


def resolve_target(fixture: dict, fixture_name: str) -> Path | None:
    for key in ("hook_path", "script_path", "target_path"):
        val = fixture.get(key)
        if val:
            val = val.replace("{{PROJECT_PATH}}", str(PROJECT_ROOT))
            return Path(os.path.expanduser(val))

    feature = fixture.get("feature", fixture_name)
    candidates = [
        PROJECT_ROOT / ".claude" / "hooks" / f"{feature}.py",
        PROJECT_ROOT / "scripts" / f"{feature}.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def run_test_case(target: Path | None, case: dict) -> tuple[bool, str]:
    stimulus = case.get("stimulus", {})
    if isinstance(stimulus, dict) and stimulus.get("file") and case.get("expected_content_contains"):
        file_path = Path(os.path.expanduser(
            stimulus["file"].replace("{{PROJECT_PATH}}", str(PROJECT_ROOT))
        ))
        if not file_path.exists():
            return False, f"file not found: {file_path}"
        try:
            content = file_path.read_text()
        except Exception as e:
            return False, f"read error: {e}"
        for needle in case["expected_content_contains"]:
            if needle not in content:
                return False, f"file content missing: {needle!r}"
        return True, "ok"

    command = case.get("command")
    if command:
        command = command.replace("{{PROJECT_PATH}}", str(PROJECT_ROOT))
    env = os.environ.copy()
    for k, v in case.get("env", {}).items():
        env[k] = str(v)

    try:
        if command:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=15, env=env, cwd=str(PROJECT_ROOT),
            )
        else:
            if target is None:
                return False, "target not found"
            stdin_data = json.dumps(stimulus) if stimulus else ""
            result = subprocess.run(
                ["python3", str(target)], input=stdin_data,
                capture_output=True, text=True, timeout=15, env=env,
            )
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT (>15s)"
    except Exception as e:
        return False, f"RUN ERROR: {e}"

    expected_exit = case.get("expected_exit_code", 0)
    if result.returncode != expected_exit:
        return False, f"exit={result.returncode} expected={expected_exit}"

    stdout_needles = case.get("expected_stdout_contains", []) or []
    output_field = case.get("expected_output_contains")
    if output_field:
        if isinstance(output_field, str):
            stdout_needles = stdout_needles + [output_field]
        else:
            stdout_needles = stdout_needles + list(output_field)

    for needle in stdout_needles:
        if needle not in result.stdout:
            return False, f"stdout missing: {needle!r}"

    for needle in case.get("expected_stderr_contains", []):
        if needle not in result.stderr:
            return False, f"stderr missing: {needle!r}"

    return True, "ok"


def sync_check() -> int:
    """--sync-check mode: report fixtures with starter_kit_status == 'pending'."""
    if not FIXTURES_DIR.exists():
        print(f"ERROR: fixtures dir not found: {FIXTURES_DIR}", file=sys.stderr)
        return 2

    pending = []
    ported = []
    skipped = []

    for fixture_path in sorted(FIXTURES_DIR.glob("*.json")):
        try:
            fixture = json.loads(fixture_path.read_text())
        except Exception:
            continue
        status = fixture.get("starter_kit_status")
        if status == "pending":
            pending.append(fixture_path.stem)
        elif status == "ported":
            ported.append(fixture_path.stem)
        elif status == "skipped":
            skipped.append(fixture_path.stem)

    print()
    print("STARTER KIT SYNC GAP")
    print("─" * 40)
    if pending:
        for name in pending:
            print(f"pending: {name} → add to infra/templates/hooks/ or mark skipped")
    else:
        print("No pending items — starter kit is in sync.")
    print()
    print(f"{len(pending)} pending | {len(ported)} ported | {len(skipped)} skipped")

    return 1 if pending else 0


def main() -> int:
    if "--sync-check" in sys.argv:
        return sync_check()

    if not FIXTURES_DIR.exists():
        print(f"ERROR: fixtures dir not found: {FIXTURES_DIR}", file=sys.stderr)
        return 2

    total_fixtures = 0
    with_tests = 0
    stubs = 0
    exempt = 0
    passed_cases = 0
    failed_cases = 0
    failures: list[tuple[str, str, str]] = []

    for fixture_path in sorted(FIXTURES_DIR.glob("*.json")):
        total_fixtures += 1
        try:
            fixture = json.loads(fixture_path.read_text())
        except Exception as e:
            print(f"Invalid JSON: {fixture_path.name} ({e})")
            continue

        test_cases = fixture.get("test_cases", [])
        is_exempt = (fixture.get("plan") == "bootstrap-exempt"
                     or fixture.get("type") == "bootstrap-exempt"
                     or fixture.get("exempt_from_fixture_runner") is True)

        if fixture.get("exempt_from_fixture_runner") is True:
            exempt += 1
            continue

        if not test_cases:
            if is_exempt:
                exempt += 1
            else:
                stubs += 1
            continue

        with_tests += 1
        target = resolve_target(fixture, fixture_path.stem)

        for case in test_cases:
            ok, msg = run_test_case(target, case)
            if ok:
                passed_cases += 1
            else:
                failed_cases += 1
                failures.append((fixture_path.name, case.get("label", "?"), msg))

    print()
    print("=" * 60)
    print("FIXTURE TEST REPORT")
    print("=" * 60)
    print(f"Total fixtures:    {total_fixtures}")
    print(f"  With tests:      {with_tests}")
    print(f"  Stubs:           {stubs}")
    print(f"  Exempt:          {exempt}")
    print()
    print(f"Test cases run:    {passed_cases + failed_cases}")
    print(f"  Passed:          {passed_cases}")
    print(f"  Failed:          {failed_cases}")

    if failures:
        print()
        print("FAILURES:")
        for fname, label, msg in failures:
            print(f"  X {fname} :: {label} -- {msg}")

    print("=" * 60)

    return 1 if failed_cases else 0


if __name__ == "__main__":
    sys.exit(main())
