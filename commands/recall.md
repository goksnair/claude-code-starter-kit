# /recall — Search past sessions

Searches the local FTS5 index of all Claude Code conversation transcripts.

## Usage

```
/recall <query>                    # search all projects
/recall <query> --project myproject # search one project only
/recall <query> --limit 15         # more results
/recall build                      # rebuild the index (run if results stale)
```

## Step 1 — Build index (first time only)

If this is your first time running /recall, build the index first:

```bash
python3 .claude/scripts/session-index.py build
```

Skip this if you've already built it. Re-run only when results seem stale.

## Step 2 — Search

```bash
python3 .claude/scripts/session-index.py search "<QUERY>" [--project <name>] [--limit <N>]
```

Replace `<QUERY>` with the user's search terms verbatim.

## Step 3 — Present results

Print the raw output. If results found, add one synthesis line:

```
Found [N] relevant passages. Most relevant: [session date + 1-line summary].
```

If no results: suggest a broader query or rebuild the index.

## Notes

- Index lives at `~/.claude/session-index.db` — local only, not committed
- Porter stemming active — "implementing" matches "implement", "implementation"
- Snippets show 32 tokens of context with `[highlighted]` terms
- To rebuild: `python3 .claude/scripts/session-index.py build`
