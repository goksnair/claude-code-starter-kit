# {{PROJECT_NAME}} — Domain Glossary

<!-- Template — fill in before use.
     Purpose: canonical definitions for terms used across this project.
     Rule: when a term appears in any agent, command, or rule file, its meaning is anchored here.
     Format: add rows to the table. "Not To Be Confused With" prevents drift between similar terms.
     Do NOT add implementation details — this is a glossary, not a spec. -->

**Last updated**: <!-- FILL IN: YYYY-MM-DD -->

---

| Term | Definition | Not To Be Confused With | Related |
|------|-----------|------------------------|---------|
| **agent** | A subagent definition in `agents/[name].md` dispatched via `Task()`. Has a name, description, model, tools, and task-specific instructions. Agents execute work. | command (a command is a user-invoked entry point; an agent executes work) | `agents/`, coordinator dispatch map |
| **command** | A user-invocable slash command in `commands/[name].md`. Triggered by typing `/name`. Runs inline or dispatches agents for heavy work. | agent (a command routes; an agent executes) | `commands/`, `/work`, `/start` |
| **memory file** | A markdown file in `.claude/memory/` that persists facts, decisions, and state across sessions. Read at `/start`. | scratch file (memory files survive sessions; scratch files are cleared at session end) | `.claude/memory/STATUS.md`, `goals.md` |
| **scratch file** | A temporary file in `.claude/scratch/` for intra-session working notes and agent state. Never committed. | memory file (scratch is ephemeral; memory is persistent) | `.claude/scratch/AGENT_STATE.json`, `WORKORDER.json` |
| **knowledge file** | A file in `knowledge/` storing domain research, frameworks, and reference material. Queryable across sessions. | memory file (knowledge is domain reference; memory is personal/project state) | `knowledge/` |
| **hook** | A Python script registered in `.claude/settings.json` that fires automatically on a Claude Code event. Hooks are guards and recorders — they do not make decisions. | command (hooks fire automatically; commands fire on user request) | `.claude/hooks/`, `.claude/settings.json` |
| **[YOUR_TERM_1]** | <!-- FILL IN: define your project-specific term here --> | <!-- FILL IN --> | <!-- FILL IN --> |
| **[YOUR_TERM_2]** | <!-- FILL IN: define your project-specific term here --> | <!-- FILL IN --> | <!-- FILL IN --> |
