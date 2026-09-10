# Postmortem: <short incident name>

**Date:** <YYYY-MM-DD> · **Severity:** <SEV_> · **Duration:** <N> minutes
**Author:** <name> · **Status:** Draft | Reviewed

## Summary

<Three sentences: what broke, who was affected, how long.>

## Impact

- Users affected: <number or %>
- Failed requests: <number>
- Data loss: <yes/no — what, and is it recoverable>
- Revenue / SLA: <if measurable; if unknown, say so and make measuring it an action item>

## Timeline

All times <TIMEZONE>.

| Time | Event |
|---|---|
| <HH:MM> | Problem began (determined retrospectively from <source>) |
| <HH:MM> | Alert fired / first report |
| <HH:MM> | Human engaged |
| <HH:MM> | Mitigated |
| <HH:MM> | Resolved |

**Time to detect:** <N> min · **Time to mitigate:** <N> min

## Root cause

<Follow the chain past the trigger to something you can actually change.>

## What went well

<Controls that worked and should be protected.>

## What made it worse

<Missing alerts, stale runbook, unclear escalation, unsafe rollback.>

## Action items

| # | Action | Type | Owner | Due | Link |
|---|---|---|---|---|---|
| 1 | <specific, verifiable> | Prevent / Detect / Reduce impact | <@name> | <date> | <ticket> |

## Runbook changes

<Which runbook entries were added or corrected as a result. At least one.>
