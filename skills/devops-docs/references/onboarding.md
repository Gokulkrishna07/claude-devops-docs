# On-call onboarding

Success criterion: a new engineer takes their first shift without needing to message anyone at 3am. Everything else is decoration.

## What it must contain

**Access checklist, verified before the first shift.** Every system they'll need, with how to request it and how to prove it works. Discovering at 3am that VPN access was never granted is the single most common on-call onboarding failure, and it is entirely preventable.

    - [ ] PagerDuty - test with a manual page to yourself
    - [ ] Cluster access - `kubectl -n <NS> get pods` returns without error
    - [ ] Break-glass DB read access - `<HOW_TO_REQUEST>`, takes 24h
    - [ ] Cloud console, read plus specific write scopes
    - [ ] Incident channel and status page

**What you own.** Which alerts route here, and explicitly which do not. Knowing what is *not* yours prevents an hour spent debugging someone else's system.

**Severity definitions with real examples from your incidents.** Generic SEV tables get ignored. "SEV1: checkout returns 5xx for all users - like the 2026-01 payment gateway incident" is usable.

**The first five minutes, as a fixed procedure.** Acknowledge the page, open the incident channel, post what you see, check for a recent deploy, find the runbook. Written as a checklist because judgement is unreliable when someone has been awake for ninety seconds.

**When to escalate, stated permissively.** New on-call engineers escalate too late, not too early. Say explicitly: "If you're not making progress after 15 minutes, escalate. This is expected, not a failure." Then name who.

**A supervised shift.** Shadow, then be shadowed. No document replaces this - the doc's job is to make the shadowing shift short.

## Ramp exercises

More effective than reading. Have them, in a non-production environment: break a service and use the runbook to fix it; roll back a deploy; find the logs for a request they can only identify by timestamp; trace a request end to end.

Each exercise that fails has found a documentation gap. That's the point - treat every question they ask during their first month as a bug report against these docs, and fix the doc rather than answering in Slack.
