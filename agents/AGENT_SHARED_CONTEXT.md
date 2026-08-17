# {{PROJECT_NAME}} — Agent Shared Context
# READ THIS FILE at the start of every agent invocation.

## Project Identity
**Project**: {{PROJECT_NAME}}
**Phase**: [update with current phase]
**Owner**: Solo — {{USER_NAME}}

## Key SSOTs (update with actual paths for this project)
- `knowledge/domain-context.md` — locked decisions + strategy
- `knowledge/cost-model.md` — financials, pricing, assumptions
- `.claude/status/SESSION_HANDOFF.md` — what was done last session
- `.claude/status/CURRENT_STATE.md` — current project state

## Branch Map
- `main` — canonical branch for all work

## Non-Negotiables for All Agents
- Cite sources for all data — no hallucinated numbers
- Distinguish: confirmed data vs. estimates vs. assumptions
- Never create new knowledge files without updating DOCUMENT_MAP.md
- Register any NEW file in `.claude/DOCUMENT_MAP.md` in same commit
- **Self-score every output**: append a Quality Score block noting data accuracy, specificity, and assumption clarity

## Canonical Output Files (stub path per agent)
| Agent | Default output stub | Created by orchestrator before dispatch |
|-------|--------------------|-----------------------------------------|
| strategy-consultant | `.claude/scratch/SC_OUTPUT.md` | Yes |
| operations-analyst | `.claude/scratch/OA_OUTPUT.md` | Yes |
| marketing-specialist | `.claude/scratch/MS_OUTPUT.md` | Yes |
| finance-analyst | `.claude/scratch/FA_OUTPUT.md` | Yes |
| research-analyst | `.claude/scratch/RA_OUTPUT.md` | Yes |
| tech-advisor | `.claude/scratch/TA_OUTPUT.md` | Yes |

Custom output files are also pre-created as stubs by the orchestrator. The task prompt will specify the exact path.

## Grilling Contract — Mandatory Pre-Question Gate

**Before asking the user ANY question**, verify it is a **decision** (only the user can make it) — not a **fact** (findable in existing files).

Check these fact sources first, in order:

1. `.claude/memory/` — STATUS.md, goals.md, preferences.md (project decisions and state)
2. `knowledge/` — domain research, cost model, technical notes
3. `.claude/projects/[project]/memory/` — reference memory files (resource IDs, engagement pointers)
4. `.claude/scratch/AGENT_STATE.json` — active task, engagement, session context

**Only ask if**: source(s) returned null OR the item is a genuine preference/judgment that cannot be inferred.
**When asking**: cite which source you checked — e.g. "I checked STATUS.md, no launch date found. What's the target date?"

**Examples:**

- ✅ DECISION (ask): "Should the onboarding flow start with goals or constraints?" — preference, not findable
- ❌ FACT (look up first): "What's the active engagement?" → check `AGENT_STATE.json` active_engagement field
- ❌ FACT (look up first): "What phase is the project in?" → check `STATUS.md` Phase field

## File Writing Protocol (CRITICAL — avoids tool permission errors)
When writing output files from agent tasks:
1. ALWAYS use the **Edit tool** to write output — never the Write tool for scratch files
2. The output file will already exist as a stub with the line: `# STUB — awaiting agent output`
3. Use Read to confirm the file exists, then Edit with:
   - `old_string="# STUB — awaiting agent output"`
   - `new_string=[your full content]`
4. Never attempt to create a net-new file with Write — pre-created stubs are always provided
5. If for any reason Edit fails, output the full content in your response so the parent session can write it
