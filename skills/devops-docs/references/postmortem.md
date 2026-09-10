# Postmortems

A postmortem exists to change the system, not to record that something happened. If it produces no change, it was theatre.

## Structure

**Summary.** Three sentences: what broke, who was affected, how long. Written for someone who will read nothing else.

**Impact, quantified.** Users affected, requests failed, revenue, data lost. "Some users experienced issues" is not impact. If the number is unknown, say it's unknown and note that measuring it is an action item - not knowing your own blast radius is itself a finding.

**Timeline.** Timestamps in a single timezone, stated explicitly. Include the moment the problem began (usually earlier than detection), when it was detected, when a human was engaged, when it was mitigated, when it was resolved. The gap between began and detected is your monitoring quality, and it is often the most valuable number in the document.

**Root cause.** Follow the chain past the proximate trigger. "A bad config was deployed" is a trigger. "A bad config was deployed because config changes bypass the staging environment, and nothing validates them at admission" is a cause. Stop when you reach something you can actually change.

**What went well.** Genuinely useful - it identifies which controls are working and should be protected.

**What made it worse.** Missing alerting, a stale runbook, an unclear escalation path, a rollback that wasn't safe. Say it plainly.

**Action items.** Each with an owner, a due date, and a tracking link. Ordered by how much they reduce risk, not by how easy they are. Distinguish "prevents recurrence" from "detects faster" from "reduces impact" - you usually want at least one of each. Vague items ("improve monitoring") are how postmortems become theatre; write "add alert on replica lag > 30s, owner @x, due 2026-04-01".

## Blamelessness in practice

Blameless does not mean vague. Name systems and decisions precisely; do not name individuals as causes. "The deploy was approved without a staging run because the pipeline permits it" is precise and blameless. "Human error" is neither - it stops the investigation exactly where it should start, and it is almost always wrong. People operate the system they were given.

## Feed it back

Every incident should produce at least one edit to a runbook. If the failure mode wasn't in the runbook, add it in the catalogue format. If it was there but the documented fix didn't work, correct it. A postmortem that doesn't update the docs guarantees the next on-call engineer starts from zero.
