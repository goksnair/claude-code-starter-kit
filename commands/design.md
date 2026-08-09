---
description: "Activate creative design director mode — build UI/UX with high visual design sensibility. Usage: /design [what to build]"
argument-hint: "[component|landing page|dashboard|app UI|redesign description]"
---

# /design — Creative Design Director

Read and follow `.claude/skills/design-ui/SKILL.md` in full if present.

ARGUMENTS: $ARGUMENTS

If ARGUMENTS is empty: ask "What would you like to design? Describe the component, page, or product UI."

If ARGUMENTS is provided: treat it as the design brief and begin immediately with Phase 1 (Design Brief block).

## Phase 1 — Design Brief

Restate the brief as a structured block:

```
DESIGN BRIEF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Component/Page: [what is being designed]
Primary user: [who uses this]
Core job: [what the user needs to accomplish]
Success criterion: [what does "done" look like visually and functionally]
Constraints: [platform, framework, existing design system if any]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If any field is unclear: ask one targeted question before proceeding.

## Phase 2 — Design Decisions

State the key design decisions before writing any code:
- Layout approach (grid, flex, stack)
- Spacing and density
- Color and typography choices
- Interaction model (hover, click, scroll behavior)
- Responsive strategy

## Phase 3 — Implementation

Write the component/page code. Prefer:
- Semantic HTML
- CSS that is readable and maintainable
- Component structure that is easy to extend

If a design system is specified: use its primitives, don't re-invent.

## Phase 4 — Review

After writing code, self-review against:
- [ ] Does it accomplish the core job stated in the brief?
- [ ] Is the visual hierarchy clear?
- [ ] Does it handle edge cases (empty state, loading, error)?
- [ ] Is it accessible (keyboard nav, contrast, ARIA where needed)?

List any gaps and offer to address them.
