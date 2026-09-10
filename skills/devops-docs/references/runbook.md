# Runbooks

A runbook is not documentation. It is an instrument someone operates while something is on fire. Optimise it for a stressed reader with degraded judgement.

## Structure

Symptom-first, always. The reader has an alert, not a curiosity.

```
1. Header           - service, owner, escalation, last verified
2. Before you start - access needed, blast radius warnings
3. Triage           - the first 90 seconds, every time, no thinking required
4. Failure modes    - one section per symptom, ordered by frequency
5. Standard ops     - deploy, rollback, scale, restart, drain
6. Escalation       - who, when, how, what to hand over
7. Appendix         - dashboards, log queries, useful one-liners
```

## The triage block

Goes at the top. The same three or four commands every time, so the reader builds muscle memory. It answers: is it up, did something just change, is it us or upstream.

```bash
# 1. Is it running?
kubectl -n <NAMESPACE> get pods -l app=<SERVICE>
# Healthy: all pods Running, RESTARTS stable, AGE > 5m

# 2. Did something just change?
kubectl -n <NAMESPACE> rollout history deploy/<SERVICE> | tail -3
# A rollout in the last 30m is your prime suspect

# 3. Is it us or upstream?
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://<HOST>/healthz
# Healthy: 200, under 0.5s
```

Follow it with a routing line: *"Recent deploy - go to Bad Deploy. Pods not Running - go to CrashLoopBackOff. Healthz slow but 200 - go to Latency."*

## Failure mode entries

This is the part people actually read. Every entry uses the same seven fields in the same order. Predictability beats elegance at 3am.

    ### <Symptom as the operator experiences it>

    **Signal:** which alert fires, or what the user reports
    **Severity:** SEV2 - checkout is down for all users
    **Likely causes** (most common first):
    1. ...
    2. ...

    **Confirm:**
    ```bash
    <command>
    ```
    > Confirmed if you see `<specific string>`. If you instead see
    > `<other string>`, this is <other failure mode> - go there.

    **Fix:**
    ```bash
    <command>
    ```
    **Blast radius:** what this touches, what breaks while it runs.
    **Verify recovery:** what to watch, for how long, before standing down.
    **If this doesn't work:** next thing to try, then escalate to <owner>.

Rules that make these work:

- **Order by observed frequency**, not severity, not alphabetically. The common case must be reachable without scrolling.
- **Every Confirm step must be able to say no.** A check that can only ever confirm is decoration. Give the reader the branch: which output means it's a different problem.
- **Separate stop-the-bleeding from fix.** Restarting a pod to restore service and finding out why it OOMed are different jobs. Label them `**Mitigate (now):**` and `**Resolve (after service is restored):**`.
- **Name the ordering constraints.** "Restart the API before the workers, or in-flight jobs get double-processed." Nothing else in the repo says this, and it is exactly what a stranger cannot guess.
- **Never write "if the issue persists, investigate further."** That is the sentence the on-call engineer is already stuck on. Name the next command or name the human.

## Standard operations

Deploy, rollback, restart, scale, drain, failover. Each needs the command, how long it normally takes, how to tell it worked, and how to abort. Rollback matters most - put it where it can be found in five seconds.

    ### Rollback
    ```bash
    kubectl -n <NAMESPACE> rollout undo deploy/<SERVICE>
    kubectl -n <NAMESPACE> rollout status deploy/<SERVICE> --timeout=180s
    ```
    Takes ~90s. This service warms its cache on boot, so don't panic at 60s.

    **Not safe if** the bad release ran a forward-incompatible migration.
    Check `<MIGRATIONS_TABLE>` first; if a migration ran, escalate to <owner>
    rather than rolling back.

That last caveat is precisely the kind of thing generated docs omit and outages are made of.

## Escalation

Concrete or useless. Name the rota, the channel, the threshold, and the handover contents.

    | When | Who | How |
    |---|---|---|
    | Any SEV1, or SEV2 over 30 min | Platform on-call | PagerDuty `platform-oncall` |
    | Suspected data loss | <name>, then Head of Eng | Phone, then #incident |
    | Cloud provider outage | Support case sev-A | <console link> |

    Hand over: what you observed, what you already tried, what you have NOT
    tried, and the incident channel link.

## Formatting for panic

- One logical action per fenced block. Someone copy-pasting six lines at once will get halfway and lose their place.
- Expected output as a comment or blockquote directly beneath the command.
- Destructive commands get a visible warning line above them, never a caveat buried mid-paragraph.
- No prose paragraph longer than three lines inside a failure mode.
- Placeholders as `<NAMESPACE>`, not `your-namespace`. Angle brackets fail loudly when unfilled; a plausible-looking string runs against the wrong cluster.

## Keeping it honest

In the header:

    > Last verified: <DATE> by <@handle>
    > Verified means every command here was run against <ENV> and produced
    > the documented output.

Runbooks that are never exercised are fiction. Mark anything you could not verify with `<!-- UNVERIFIED -->` and say so in the handover. Recommend re-verification after any architecture change.

See `failure-modes.md` for a starter catalogue already written in this format.
