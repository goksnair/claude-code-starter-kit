# Changelog

## [0.2.0] 2026-08-16 (current)

### Added
- `KIT_VERSION` file — enables upgrade detection and version tracking
- `--upgrade` flag on `install.sh` — safe upgrade with settings merge and backup
- `scripts/verify-install.sh` — end-to-end test for fresh install and upgrade paths
- `hooks/implementation-audit.py` — Stop hook: warns when infra files written but not tested
- `hooks/workflow-injector.py` — UserPromptSubmit: research/knowledge workflow suggestions
- `scripts/check-hooks-exist.sh` — validates all hooks in settings.json exist on disk
- `scripts/run-fixture-tests.py` — SDLC fixture test harness with `--sync-check` flag
- `.claude/tests/fixtures/` — 3 sample fixtures (memory-validator, bash-tool-guard, session-start)
- `UPGRADE.md` — this upgrade guide
- `CHANGELOG.md` — this file

### Changed
- `install.sh` — now writes `KIT_VERSION` on install; added `--upgrade` mode
- `README.md` — added Upgrade section and version line

## 2026-08-09 (phase 1-4 release)

### Added
- `/onboard` command + `CLAUDE_ONBOARDING.md` — guided first-session setup
- `/recall`, `/query`, `/pivot`, `/setup-check` commands
- `/dump`, `/lock`, `/week`, `/status` commands
- `hooks/git-recent-wins.py` — surfaces recent git wins at session end
- `hooks/skill-body-size-guard.py` — enforces skill file size limits
- `hooks/wiki-ingest-guard.py` — validates wiki file format on write
- `SETUP_PHASES.md` — phase-by-phase setup guide
- `REPO_MAP.md` — codebase map for Claude context
- Non-interactive install mode (`--non-interactive`, `--print-plan`)
- `score-starter-kit.sh` — benchmark scorer (10 dimensions, 100-point scale)

### Changed
- Renamed "engagement" → "project" throughout (hooks, commands, install, README)
- `memory-routing.md` added to rules/

## 2026-06-22 (initial release)

- 23 hooks covering session lifecycle, guards, validators
- 50+ slash commands
- Memory architecture (STATUS.md, goals.md, SESSION_HANDOFF.md)
- Agent whitelist pattern
- CLAUDE.md template with behavioral rules
