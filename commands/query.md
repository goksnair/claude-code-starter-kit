# /query — Search the knowledge wiki

Searches wiki pages in `knowledge/wiki/` for a topic.

## Usage

```
/query <topic>
/query <topic> --file <wiki-page>
```

## Steps

1. Run a grep across `knowledge/wiki/`:

```bash
grep -ri "<TOPIC>" knowledge/wiki/ --include="*.md" -l
```

2. For each matching file, read the relevant section (grep -A 5 -B 2).

3. Synthesise findings into a 3-5 line answer. Cite the wiki page.

If nothing found: say so clearly and suggest adding a wiki entry with `/capture`.

## Notes

- Wiki pages live at `knowledge/wiki/<domain>.md`
- Starter pages: claude-ops.md (system notes), projects.md (active work)
- Add new pages as your knowledge base grows
- `/capture [fact]` routes new facts to the right wiki page automatically
