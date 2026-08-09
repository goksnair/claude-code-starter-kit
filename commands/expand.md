---
description: "Expand a profile, document, or knowledge file by discovering competencies or insights hidden in related sources. Additive only — never modifies existing content."
argument-hint: "[what to expand: profile, knowledge file, or domain]"
---

# /expand — Discovery and Expansion from Sources

You are enriching an existing file by discovering relevant items hidden in documents, online sources, and related files. This command is additive only — it never modifies existing content, only extends it.

Follow these steps exactly in order. Do not skip steps.

---

## Step 0: Read Existing Files

Read the target file(s) before doing anything else. You must know what is already there so you do not propose duplicates.

Hold this content in context throughout the command. Do not re-read these files later.

---

## Step 1: Discovery — Scan All Sources

Scan every available source for relevant items. Process sources in this order:

### 1a. Local documents
Read all files in the relevant documents directory. Extract:
- Every item that implies skill, knowledge, competency, or insight
- Specific named tools, methods, or outcomes
- Any cross-reference to related topics

### 1b. Online sources (if applicable)
For each item discovered that references an online resource:
1. Fetch the resource
2. Extract the relevant competency or insight it implies

### 1c. Related files in the project
Check `knowledge/` subdirectories for any files related to the expansion target. Extract any cross-references not already in the target file.

---

## Step 2: Enrichment

For each discovered item, extract what it implies:
- What problem domain does this address?
- What methods or skills does someone need to do this work?
- What is the standard approach for this kind of work?

---

## Step 3: Build Expansion Map

After enriching all items, build a deduplicated expansion map. Group findings by category relevant to your domain.

For each item, record:
- The item name
- The source it came from
- Whether it was found directly or inferred

Remove anything already present in the target file.

---

## Step 4: Present for Review

Present all new items for the user's review before writing anything:

```
## /expand found [N] new items across [M] sources

**[CATEGORY 1]**
Source: [source name]
  + [Item 1]
  + [Item 2]

**[CATEGORY 2]**
Source: [source name]
  + [Item 1]
```

Then ask:
> **How would you like to proceed?**
> - `all` — Add everything above
> - `review` — Walk through each source group one at a time
> - `skip` — Cancel without writing anything

Wait for the user's response before writing anything.

---

## Step 5: Write Confirmed Additions

Apply only the confirmed items. Use the Edit tool to add to relevant sections — do not rewrite entire files.

For each addition, add a brief source annotation: *(Source: [name])* — this makes future `/expand` runs idempotent.

---

## Step 6: Summary Report

After writing:

```
## /expand Complete

### Added to [file]
[List each item added, with source]

### Sources processed
[List each source and how many items it yielded]

### Sources skipped
[Any sources missing, empty, or yielding nothing new — with brief reason]
```

---

## Design Principles

- **Additive only.** Never modify existing content.
- **Source-traceable.** Every addition records where it came from.
- **User confirms before writing.** Full map is shown and confirmed before any file is touched.
