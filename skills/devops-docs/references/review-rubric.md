# Review rubric

Use before handing over a document, and when the user asks for existing documentation to be reviewed or trimmed. Report honestly which checks fail - a review that passes everything is not a review.

## Blocking checks

Any failure here means the document is not ready.

1. **Every command is real.** No invented flags, paths, metric names, or dashboard URLs. Anything unverified is marked `<!-- UNVERIFIED -->` or left as a TODO. Wrong commands get run; they are worse than absence.
2. **Placeholders are visible.** `<ANGLE_BRACKETS>`, not plausible-looking real-ish values.
3. **Destructive actions carry a blast-radius note** above them, not buried.
4. **The document names a human.** Ownership and escalation are present and specific.
5. **No fabricated specifics.** No invented thresholds, SLAs, team names, or timings presented as fact.

## Quality checks

6. **The cold-pager test.** Could a competent engineer who has never seen this system use it under pressure? Read it as that person, not as someone who already knows the answers.
7. **Nothing explains general technology.** No Docker/Kubernetes/CI primers.
8. **Nothing narrates the code.** Every claim tells the reader something the source doesn't.
9. **Symptom-first ordering** in anything operational.
10. **Expected output present** for every diagnostic command.
11. **Failure paths documented**, not just the happy path.
12. **Within its length budget**, and the length is doing work.
13. **No filler sections** - no empty Prerequisites, no generic Best Practices, no Conclusion, no N/A-filled tables.
14. **Surprising things are explained.** Anything that looks wrong but is right has a one-line reason.
15. **Dated and attributed.**

## The deletion pass

Go through the draft once with the only goal of removing text. For each paragraph, ask which of these it answers:

- What breaks, and how do I know?
- What do I do about it?
- What will this action break?
- Who do I call?
- Why is it built this way?

If a paragraph answers none of these, delete it. Most first drafts lose 30-50% here and get better. Expect this - the goal is a document someone finishes reading.

## Reviewing AI-generated documentation

Generated ops docs fail in recognisable ways. Scan for these first:

| Pattern | What to do |
|---|---|
| Tool tutorials (what Docker is, what CI/CD means) | Delete outright |
| Plausible commands with invented flags | Verify each one, or mark unverified |
| "Prerequisites: familiarity with the command line" | Delete |
| Generic "Best Practices" / "Security Considerations" | Delete, unless a specific claim about this system is buried inside - extract it |
| Every config value listed with its default and no reasoning | Keep only the non-obvious ones, add the why |
| Happy path only | Flag as the main gap; this is usually the biggest one |
| Tables padded with N/A | Delete the table or the columns |
| Confident thresholds and SLAs nobody agreed to | Convert to TODOs - these are the most dangerous items in the doc, because they read as authoritative |
| Emoji headers, "In conclusion", "In today's fast-paced world" | Delete |

**Preserve before you cut.** Extract every verified fact - service names, real commands, thresholds, ownership, links - then rebuild from the template. Bloated docs usually contain a small amount of genuine knowledge; losing it while removing the padding is the one unrecoverable mistake in this process.

Report the before/after line count and list what was removed, so the user can object if something mattered.
