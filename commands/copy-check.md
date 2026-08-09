# Copy Quality Index
**Version**: 1.0
**Purpose**: Gate any copy (website, email, SOP, pitch, blog, social, investor materials) before it ships. All 24 core checks must pass. Section D is project-specific — customize per project.
**SSOT**: This file. Do not score copy in chat — score it against this index.

---

## Scope — Every Content Type Covered

This index applies to ALL written output without exception:

- Website copy (all pages, landing pages, CTAs)
- Blog posts and articles
- Social media posts (LinkedIn, Instagram, WhatsApp broadcast messages)
- Email: customer-facing AND internal communications that represent company position
- SOPs and operational documents
- Pitch decks and investor materials
- Customer-facing documents (welcome kits, agreements, proposals)
- Any written output produced by or on behalf of this project

**Excluded**: Internal working notes, scratch analysis, financial model annotations, code comments, one-line team messages.

---

## How to Use

Score each piece of copy before it is approved for use. Assign PASS / FLAG / FAIL per check.
- **PASS**: Check is fully satisfied
- **FLAG**: Borderline — needs human review and possible revision
- **FAIL**: Hard block — copy must be rewritten before use

Core checks (A+B+C+E): **24 checks**. Copy passes when **>=22 PASS, 0 FAIL**.
Section D (project-specific): Add checks per project. Score separately if used.

---

## Section A — Vocabulary Red Flags (AI Tells)

These words/phrases are statistically overrepresented in AI-generated text. Overuse is the failure — thresholds are per piece of copy (homepage section, email, blog post).

| # | Check | Threshold | How to Test |
|---|-------|-----------|-------------|
| A1 | **Em-dash (—) overuse** | Max 1 per 300 words | Count em-dashes. Flag if more than 1 per 300 words. |
| A2 | **Banned adjectives** present: *seamlessly, comprehensive, robust, tailored, ensure, leverage, cutting-edge, holistic, transformative, innovative* | 0 occurrences | Grep for each. One instance = FAIL. |
| A3 | **Filler metaphors**: *delve into, dive into, unpack, navigate (used metaphorically), unlock potential* | 0 occurrences | These are LLM verbal tics. Never appear in human premium copy. |
| A4 | **Transition stacking**: *Furthermore, Moreover, Additionally, Nevertheless* in rapid succession (2+ in same section) | 0 stacks | One use is fine. Two in a row = FAIL. |
| A5 | **Cliche closers**: *At the end of the day, In conclusion, It's worth noting, It's important to note, Needless to say* | 0 occurrences | Absolute ban. These read as filler. |
| A6 | **Round numbers only** — 50%, 75%, 100% with no specific figures | Flag if no specifics in copy | Real copy uses specifics. Generic % signals AI authorship. |

---

## Section B — Structural Red Flags

| # | Check | Threshold | How to Test |
|---|-------|-----------|-------------|
| B1 | **Bullet-point overuse** — emotional or narrative content bulleted when prose would be more human | 0 bullets in emotional/narrative sections | Testimonials, empathy sections, brand story — prose only. Service lists = bullets are fine. |
| B2 | **Paragraph uniformity** — every paragraph is exactly 2-3 sentences | Paragraphs should vary | Read aloud. Uniformity = robotic. One-sentence punches and longer paragraphs must coexist. |
| B3 | **Perfectly parallel headings** — all H2s start with the same word type or structure | Flag if all parallel | Natural variation is human. |
| B4 | **Rhetorical questions as manipulative hooks** — "Don't your customers deserve the best?" | 0 instances | Emotional manipulation reads as cheap. Frame as confidence, not pressure. |
| B5 | **Section summary sentences** — each section ends by restating what it just said | 0 restatements | Cut the last sentence of any section that merely summarises what the section said. |

---

## Section C — Tone and Voice Red Flags

| # | Check | Threshold | How to Test |
|---|-------|-----------|-------------|
| C1 | **No warmth, humor, or personality** — copy is earnest, solemn, and uniform throughout | At least 1 moment of warmth or personality per page | Premium brands have a voice — not clinical professionalism. |
| C2 | **Lacks specificity** — generic examples, no local texture, no real detail | 1+ specific, grounded detail per section | Bad: "Our team helps your customers." Good: a specific time, number, name, or situation. |
| C3 | **No cultural or contextual grounding** — copy that could apply to any company in any country | At least 1 contextually grounded reference per page | Copy portable to any market fails this check. |
| C4 | **Passive voice concentration** — "Care is provided", "families are served", "updates are sent" | <20% passive sentences per section | Read and count. Heavy passive = distant, institutional. |
| C5 | **Opinion and point of view absent** — hedges everything with *may, might, could, perhaps* | 0 hedge clusters | "We might be able to help" = FAIL. "We're there" = PASS. Own the claim or don't make it. |

---

## Section D — Project Brand-Specific Checks

**This section is customized per project.** Replace these placeholder checks with brand-specific gates before using this index on a new project.

| # | Check | Threshold | How to Test |
|---|-------|-----------|-------------|
| D1 | **[Brand claim without proof]** — core value proposition stated without a specific signal to support it | 0 unsupported claims | Replace with the brand's key claim and what constitutes evidence for it. |
| D2 | **[Wrong positioning frame]** — copy frames the brand as reactive or generic rather than the intended positioning | 0 instances | Define the specific positioning violation for this project. |

*Add D3, D4 etc. as needed. Delete placeholders when not applicable.*

---

## Section E — AI-Detection Markers

Derived from detection methodology used by Originality.ai, GPTZero, Turnitin, Writer.ai, Copyleaks, and peer-reviewed linguistics research on AI-generated text.

| # | Check | What AI-Detection Tools Flag | Threshold / How to Test | PASS / FLAG / FAIL Criteria |
|---|-------|------------------------------|-------------------------|------------------------------|
| E1 | **Sentence length uniformity (burstiness failure)** | GPTZero's primary signal. Human writing has high variance in sentence length. AI produces a "smooth" rhythm where most sentences fall within a narrow band (15-25 words). | Count word length of every sentence. If 70%+ fall within a 10-word band: FLAG. If 80%+: FAIL. | PASS: Wide variation — sentences range 5 to 35+ words. FLAG: Narrow range in most paragraphs. FAIL: Nearly all sentences are the same length; metronomic cadence when read aloud. |
| E2 | **Predictable word choice (low perplexity)** | AI always chooses the most probable next word. Copy feels correct but never interesting — no unexpected verb, no specific proper noun, no unconventional phrasing. | Read each paragraph: does any word or phrase surprise you in a good way? Is there a verb more precise than the obvious choice? | PASS: At least 1 unexpected, precise, or vivid word choice per 150 words. FLAG: Accurate but all word choices are statistically obvious. FAIL: Every sentence uses the most predictable phrasing — no voice. |
| E3 | **Abstract noun saturation (nominalization overuse)** | Turnitin research: AI converts verbs into abstract nouns. "We coordinate" becomes "our coordination efforts". Adds length without meaning. | Count abstract nouns (-tion, -ment, -ance, -ity, -ness, -ence) per 100 words. Above 8: FLAG. Above 12: FAIL. Also flag sentences where main verb = "be" + nominalization. | PASS: Rate below 8 per 100 words. Active verbs carry meaning. FLAG: Rate 8-12 per 100 words. FAIL: Rate above 12, or main verb is mostly "be" + abstract noun. |
| E4 | **Uniform information density** | Human writing has uneven information density — peaks of high-content sentences surrounded by lower-density connective tissue. AI distributes information evenly. | Mark each sentence H (new info, specific claim, detail) or L (connective tissue, transition, filler). Flag mechanical alternation or all-H with no breathing room. | PASS: H and L alternate naturally with variation. FLAG: Density is noticeably even — every sentence feels the same weight. FAIL: Mechanical H-L-H-L or all-H with no breathing room. |
| E5 | **Absence of field-specific, observable detail** | AI produces statistically averaged descriptions plausible but belonging to no specific time, place, or person — no "experiential anchoring". | Does this copy contain at least 1 detail that is (a) role-specific or context-specific, (b) observable rather than inferred, (c) not findable by searching the internet? | PASS: At least 1 grounded, observable, role-specific detail per 400 words. FLAG: Copy is plausible but all examples are generic composites. FAIL: No specific observable detail anywhere. |
| E6 | **Epistemic hedge clustering** | AI overuses hedging because training data penalised overconfident claims: "it is important to note", "one might consider", "in many cases", "often", "typically". These are evasive and erode trust. | Count hedge phrases per 500 words. Above 4: FLAG. Above 7: FAIL. Also flag service claims hedged with "might" or "may" when evidence exists. | PASS: 0-4 hedge phrases per 500 words. Claims are made directly. FLAG: 4-7 per 500 words — copy feels uncertain. FAIL: More than 7 per 500 words. |
| E7 | **Symmetric argument structure** | AI reliably produces balanced "on one hand... on the other hand" constructions even when the topic does not require balance. Humans take positions. | Flag: "on one hand... on the other", "while X is important, Y must also be considered", "both A and B play a role" in marketing/customer copy. Acceptable in investor analysis. | PASS: Marketing copy takes a position without artificial balance. FAIL: Symmetric construction present in marketing, website, social, or email copy. FLAG: Symmetric structure in investor/analytical content — acceptable but noted. |
| E8 | **Generic cultural/contextual placeholder** | AI defaults to universal descriptions, averaging across training data. Copy about the product or service sounds like it could apply to any company in any market. | Remove the brand name. Would this copy still make sense for a generic competitor in a different market? If yes: FAIL. | PASS: Copy is not portable — uses context-specific details, names, settings, or emotional frames. FLAG: Mostly generic with one or two specific references. FAIL: Fully portable — no specific detail. |

---

## Scoring Sheet Template

```
Copy: [Title / Description]
Date: [YYYY-MM-DD]
Reviewer: [Name or "Claude"]
Content type: [website / blog / social / email-customer / email-internal / SOP / pitch / investor / other]

--- Section A: Vocabulary ---
A1 Em-dash:              [ PASS / FLAG / FAIL ]
A2 Banned adjectives:    [ PASS / FLAG / FAIL ]
A3 Filler metaphors:     [ PASS / FLAG / FAIL ]
A4 Transition stack:     [ PASS / FLAG / FAIL ]
A5 Cliche closers:       [ PASS / FLAG / FAIL ]
A6 Round numbers:        [ PASS / FLAG / FAIL ]

--- Section B: Structure ---
B1 Bullet overuse:       [ PASS / FLAG / FAIL ]
B2 Para uniformity:      [ PASS / FLAG / FAIL ]
B3 Heading parallel:     [ PASS / FLAG / FAIL ]
B4 Rhetorical hooks:     [ PASS / FLAG / FAIL ]
B5 Section restate:      [ PASS / FLAG / FAIL ]

--- Section C: Tone and Voice ---
C1 Warmth/voice:         [ PASS / FLAG / FAIL ]
C2 Specificity:          [ PASS / FLAG / FAIL ]
C3 Cultural grounding:   [ PASS / FLAG / FAIL ]
C4 Passive voice:        [ PASS / FLAG / FAIL ]
C5 Hedging:              [ PASS / FLAG / FAIL ]

--- Section D: Project Brand Checks ---
D1 [Brand claim proof]:  [ PASS / FLAG / FAIL ]
D2 [Positioning frame]:  [ PASS / FLAG / FAIL ]
(Add D3+ per project)

--- Section E: AI-Detection Markers ---
E1 Sentence length var:  [ PASS / FLAG / FAIL ]   Note: ___
E2 Word choice predict:  [ PASS / FLAG / FAIL ]   Note: ___
E3 Abstract noun rate:   [ PASS / FLAG / FAIL ]   Rate per 100 words: ___
E4 Info density pattern: [ PASS / FLAG / FAIL ]   Note: ___
E5 Field-specific detail:[ PASS / FLAG / FAIL ]   Detail cited: ___
E6 Hedge cluster rate:   [ PASS / FLAG / FAIL ]   Rate per 500 words: ___
E7 Symmetric argument:   [ PASS / FLAG / FAIL ]   Note: ___
E8 Cultural placeholder: [ PASS / FLAG / FAIL ]   Note: ___

--- RESULT (Core 24 checks) ---
PASS count: __ / 24
FLAG count: __  (overrides with reason below)
FAIL count: __

RESULT: [ PASS >=22 PASS, 0 FAIL | CONDITIONAL — FLAG review required | REWRITE ]

FLAG override reasons (if any):
[Check]: [Written reason for override] — Approved by: [Name] on [Date]

Notes:
```

---

## Quick Reference — Instant Red Flag Words

Ban outright (0 tolerance):
> seamlessly, comprehensive, robust, tailored (as adj), leverage, ensure, holistic, transformative, cutting-edge, innovative, delve into, dive into, unpack, Furthermore/Moreover (consecutive), In conclusion, It's worth noting, Needless to say, at the end of the day

Watch carefully (flag if overused):
> trusted, dedicated, proactive, curated, thoughtful, expertise, solutions, premium (without proof)

AI-detection watch list (flag if clustered):
> it is important to note, one might consider, this suggests that, in many cases, often, typically, generally, it can be said, it is worth mentioning, on one hand, on the other hand

---

## Notes on Punctuation

- **Em dash (—)**: one per 300 words maximum. Never use as a sentence connector in consecutive sentences.
- **Oxford comma**: use consistently within the same document.
- **Ellipsis (...)**: only in quoted speech. Never as a dramatic pause device in marketing copy.
- **Exclamation marks**: avoid in professional/brand copy. The brand should be confident, not excited.
- **ALL CAPS for emphasis**: 0. Use bold or sentence structure for emphasis.

---

## How to Run (Claude Code)

1. Paste the copy into Claude Code: `run /copy-check`
2. Claude reads this file, scores against all checks, returns a completed scoring sheet
3. Any FAIL result = mandatory rewrite of the failed section before proceeding
4. FLAG results may be overridden with a written reason recorded in the score sheet
5. >=22 PASS, 0 FAIL = approved

Do not score copy from memory. Scores made without referencing this file are not valid.

### Failure Output Format (FAIL and FLAG results)

For every FAIL or FLAG, the scoring sheet MUST include a structured failure block immediately after the check line:

```text
[CheckID] [FAIL/FLAG]
  Offending text: "[exact phrase or sentence that triggered the check]"
  Rule violated: [check name, e.g. "A2 Banned adjectives", "E6 Hedge cluster"]
  Fix: [one concrete rewrite suggestion — not "remove it", but "replace with X"]
```

Example:

```text
A2 Banned adjectives: FAIL
  Offending text: "our comprehensive approach to senior care"
  Rule violated: A2 — "comprehensive" is on the banned adjective list
  Fix: Replace with a specific claim — "our 6-step intake process" or "care across 14 service areas"
```

Counts alone (e.g. "3 FAIL") are not valid output. Every FAIL and FLAG requires a failure block.

---

*Generic starter kit version — Section D must be customized per project.*
