# Contributing

## The most useful contribution

New entries in `references/failure-modes.md`. Something that has actually bitten you in production beats anything generated from general knowledge, and this file gets more valuable with every real one added.

Use the existing seven-field format:

```markdown
### <Symptom as the operator experiences it>

**Signal:** <alert or user report>
**Likely causes** (most common first):
1. ...

**Confirm:**
```bash
<command>
```
> <what output confirms it, and what output means it's something else>

**Fix:**
```bash
<command>
```
**Blast radius:** <what this touches>
**Verify recovery:** <what to watch, for how long>
**If this doesn't work:** <next step, then escalate>
```

Requirements for a failure mode entry:

1. **Every command must be one you have actually run.** Not one you're confident about — one you have run. This is the whole premise of the skill; a wrong command here propagates into other people's runbooks.
2. **The Confirm step must be able to return "no."** A check that can only ever confirm is decoration. Give the branch.
3. **Causes ordered by real-world frequency**, not by severity.
4. **Blast radius is mandatory** on anything destructive.
5. **Vendor-neutral where possible.** Cloud-specific entries are welcome but should say which provider in the heading.

## Changing the rules in SKILL.md

The do/don't lists are opinionated on purpose, and each line is there because it fixes an observed failure in generated documentation. If you want to add or remove one, say in the PR which real failure it addresses. "This seems like good practice" is not enough — the list stays short by rejecting generically true advice, which is exactly what the skill tells Claude not to write.

## Testing a change

Point Claude at a real repo with the modified skill and have it produce a runbook. Then read the output as the cold pager: a competent engineer, no knowledge of that system, 3am. If you can't act on it, the change didn't work.

Include a before/after sample in the PR when changing anything that affects output shape.

## Scope

In scope: operational and infrastructure documentation. Out of scope: API reference generation, code comments, end-user product documentation, marketing content. Those are different problems with different readers, and widening the scope would dilute the reader model that makes this work.

## Contributing to the safety harness

Two files enforce the credential rules: `references/SAFETY.md` (instructions) and `scripts/safe_inventory.py` (a denylist in code). Additions to either are welcome and reviewed quickly.

If you know a filename convention that holds secrets and isn't on the denylist, that's a one-line PR worth opening. Cover the tool and the convention in the commit message so the next person knows why the entry exists.

For `scripts/check_doc.py`, new credential patterns should come with a test string in the PR description that the current version misses. Keep patterns specific — a regex that fires on every occurrence of the word "token" trains people to ignore the tool, which is worse than not having it.

## Contributing to cost guidance

Do not add prices to `assets/data/cost-anchors.csv` in a pull request. It ships unpopulated on purpose: a committed price table goes stale immediately and contradicts the rule the skill exists to enforce. Contributions to `references/cost.md` about *how* to source and caveat a figure are welcome — particularly additions to the list of costs that surprise people.

## Scripts

Standard library only. No network calls. No installing anything on the user's machine — if a tool is missing, print the command and exit. These constraints are the point, not an inconvenience to route around.
