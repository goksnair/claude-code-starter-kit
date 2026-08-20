# Upgrading the Claude Code Starter Kit

## Check your installed version

```bash
cat KIT_VERSION
```

If this file doesn't exist, you have a pre-2026-08-16 install. Follow the "Manual upgrade" section below.

## Standard upgrade (2026-08-16 or later)

You have `KIT_VERSION` in your project root. Run:

```bash
# From the starter kit templates directory
bash install.sh --upgrade ~/path/to/your-project
```

This will:
1. Back up your existing `.claude/settings.json` to `.claude/settings.json.backup-YYYYMMDD`
2. Copy new command files (skips files you already have)
3. Copy new hook `.py` files (skips files you already have)
4. Copy new agent files (skips files you already have — your coordinator.md is never overwritten)
5. Merge new hooks and permissions into your `settings.json` — your custom entries are preserved
6. Copy `score-starter-kit.sh` if not present in your project
7. Show suggested CLAUDE.md @-rules additions (does not auto-write)
8. Update `KIT_VERSION`

After upgrading, run the verification script:

```bash
bash score-starter-kit.sh
```

## I already have a Claude Code setup (no KIT_VERSION)

If you built your setup independently (custom /start, /work, /end, your own hooks), use this path:

1. Run `bash detect-and-route.sh` to confirm your upgrade route
2. Run `bash install.sh --upgrade --selective [your-project-path]` — copies only files you don't have, prompts before each
3. Run `bash score-starter-kit.sh` to verify your setup score
4. Review any CLAUDE.md @-rules suggestions printed during upgrade — add the ones you want manually

Your existing commands, coordinator, and CLAUDE.md are never overwritten.

## Manual upgrade (pre-2026-08-16 installs — no KIT_VERSION file)

1. **Back up your settings**: `cp .claude/settings.json .claude/settings.json.backup`
2. **Back up your memory files**: `cp -r .claude/memory/ .claude/memory.backup/`
3. **Run fresh install into a temp dir**: `bash install.sh --non-interactive MyKit /tmp/kit-fresh "Your Name"`
4. **Diff your settings against the fresh one**: `diff .claude/settings.json /tmp/kit-fresh/.claude/settings.json`
5. **Manually merge**: copy any hooks from the fresh `settings.json` that aren't in yours into your file
6. **Copy new hook files**: `cp /tmp/kit-fresh/.claude/hooks/*.py .claude/hooks/`
7. **Copy new command files**: `cp /tmp/kit-fresh/.claude/commands/*.md .claude/commands/`
8. **Verify**: `bash score-starter-kit.sh`

## What to expect after upgrading

- Your memory files (`.claude/memory/`) are never touched by upgrade — they are yours
- Your `settings.json` customizations are preserved via merge
- New hooks are added to your hooks directory automatically
- Run `bash scripts/check-hooks-exist.sh` to confirm all hooks in settings.json exist on disk
- Run `python3 scripts/run-fixture-tests.py --sync-check` to see if any new hooks need review

## After upgrading: populate your memory files

To set up structured memory after upgrading, run:

```
/onboard --from-project .
```

This scans your existing project and populates `goals.md` and `STATUS.md` without reinstalling anything.

## Rolling back

Your backup is at `.claude/settings.json.backup-YYYYMMDD`. To roll back settings:

```bash
cp .claude/settings.json.backup-YYYYMMDD .claude/settings.json
```
