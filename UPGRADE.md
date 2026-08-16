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
2. Copy all updated hook `.py` files (your hooks directory is managed by the kit — customizations go in `settings.json`, not hook files)
3. Merge new hooks and permissions into your `settings.json` — your custom entries are preserved
4. Update `KIT_VERSION`

After upgrading, run the verification script:

```bash
bash scripts/verify-install.sh
```

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

## Rolling back

Your backup is at `.claude/settings.json.backup-YYYYMMDD`. To roll back settings:

```bash
cp .claude/settings.json.backup-YYYYMMDD .claude/settings.json
```
