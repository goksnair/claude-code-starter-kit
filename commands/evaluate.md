---
description: "Output quality gate. Scores any agent output against a universal rubric. Returns APPROVED or BLOCKED with evidence."
argument-hint: "output file to evaluate — or leave blank to evaluate last file written"
---

# /evaluate — Output Quality Gate

## Universal Rubric (100 points)

| Dimension | Weight | What to check |
|-----------|--------|---------------|
| Accuracy | 30% | Facts, numbers, file paths are correct and sourced |
| Completeness | 25% | All requested outputs delivered, nothing missing |
| Format | 20% | Follows conventions, readable, correct markdown |
| SSOT compliance | 25% | Sensitive data not in wrong files, routing rules followed |

**Threshold**: ≥ 0.70 = APPROVED | < 0.70 = BLOCKED

---

## Step 1 — Identify output to evaluate

If $ARGUMENTS is provided: read that file.

If blank: check what was most recently written in this session (from conversation context).

## Step 2 — Identify output type and apply domain gate

### Knowledge / wiki page gate

- [ ] No personal or sensitive data
- [ ] All market claims flagged `UNVALIDATED` if from single source
- [ ] Sources section populated
- [ ] Cross-references present where relevant

### Copy / external communication gate

- [ ] Run `/copy-check` — must score ≥ 22 PASS, 0 FAIL
- [ ] No PII exposed
- [ ] Brand voice consistent

### Configuration / spec file gate

- [ ] No hardcoded secrets or personal paths
- [ ] Deadlines are absolute dates (not "next week")
- [ ] Actions are specific (person, file, target)

## Step 3 — Score and verdict

Calculate weighted score. Print:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVALUATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Output:     [file path]
Type:       [knowledge | copy | config | other]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Accuracy:       [score]/0.30 — [evidence]
Completeness:   [score]/0.25 — [evidence]
Format:         [score]/0.20 — [evidence]
SSOT:           [score]/0.25 — [evidence]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Domain gate:    [PASS | FAIL — list failed checks]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL: [score]/1.00

[APPROVED ✅ | BLOCKED ⛔]
[If BLOCKED: exact issues that must be fixed before this file is used]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
