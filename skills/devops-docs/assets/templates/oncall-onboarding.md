# On-call onboarding: <TEAM>

Goal: your first shift without needing to message anyone at 3am.

## Access checklist — complete before your first shift

Each item includes how to verify it actually works. Do not tick anything you have not tested.

- [ ] PagerDuty — send yourself a test page
- [ ] Cluster access — `kubectl -n <NS> get pods` returns without error
- [ ] Cloud console — <scopes needed>
- [ ] Break-glass DB read — request via <HOW>, takes <N>h
- [ ] Incident channel <#CHANNEL> and status page <link>
- [ ] VPN — <verification command>

## What you own

**Alerts routed to you:** <list>
**Explicitly not yours:** <list, and who owns them>

## Severity levels

| Level | Means | Real example |
|---|---|---|
| SEV1 | <definition> | <an actual incident of ours> |
| SEV2 | <definition> | <an actual incident of ours> |

## First five minutes

1. Acknowledge the page.
2. Open <#CHANNEL>, post what you see. Do this before investigating — it starts the clock for everyone else.
3. Check for a recent deploy: `<command>`
4. Open the runbook for the alerting service: <index link>
5. Follow triage. Post what you find as you go.

## Escalating

**If you are not making progress after 15 minutes, escalate.** This is expected and not a failure — late escalation is the more common and more costly mistake.

| Situation | Escalate to | How |
|---|---|---|
| <situation> | <name/rota> | <method> |

## Ramp exercises

Complete in <NON_PROD_ENV> before your first shift:

- [ ] Break <service> and restore it using only the runbook
- [ ] Roll back a deploy
- [ ] Find logs for one request given only a timestamp
- [ ] Trace a request end to end through every hop

Every question you had to ask during these is a documentation gap. Please fix the doc rather than just getting your answer.
