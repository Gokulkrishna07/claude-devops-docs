# Runbook: <SERVICE_NAME>

> **Owner:** <TEAM> · **On-call:** <ROTA> · **Channel:** <#CHANNEL>
> **Last verified:** <YYYY-MM-DD> by <@handle> — every command below was run against <ENV>.

## Before you start

**You need:** <access requirements — cluster, VPN, DB, cloud console>
**Announce in <#CHANNEL> before** any restart, scale, or rollback during business hours.

## Triage — first 90 seconds

```bash
# 1. Is it running?
kubectl -n <NAMESPACE> get pods -l app=<SERVICE>
# Healthy: all Running, RESTARTS stable, AGE > 5m

# 2. Did anything just change?
kubectl -n <NAMESPACE> rollout history deploy/<SERVICE> | tail -3
# A rollout in the last 30m is your prime suspect

# 3. Is it us or a dependency?
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://<HOST>/healthz
# Healthy: 200, under <N>s
```

**Route from here:** recent deploy → [Bad deploy](#bad-deploy). Pods not Running → [Crash loop](#crash-loop). 200 but slow → [Latency](#latency).

---

## Failure modes

### <Symptom as the operator sees it>

**Signal:** <alert name, or what users report>
**Severity:** <SEV_ and the user-facing consequence>

**Likely causes** (most common first):
1. <cause>
2. <cause>

**Confirm:**
```bash
<command>
```
> Confirmed if `<string>`. If instead `<other string>`, this is <other mode> — go there.

**Mitigate (now):**
```bash
<command>
```
**Blast radius:** <what this touches, what breaks while it runs>

**Resolve (after service is restored):** <the actual fix>

**Verify recovery:** <what to watch, for how long>

**If this doesn't work:** <next step>, then escalate to <owner>.

---

<!-- Repeat the block above per failure mode. Order by observed frequency. -->

## Standard operations

### Deploy
```bash
<command>
```
Takes ~<N>. Success looks like: <what>.

### Rollback
```bash
kubectl -n <NAMESPACE> rollout undo deploy/<SERVICE>
kubectl -n <NAMESPACE> rollout status deploy/<SERVICE> --timeout=<N>s
```
Takes ~<N>. **Not safe if** <condition — e.g. a forward-incompatible migration ran>; in that case escalate to <owner> instead.

### Restart / Scale / Drain
```bash
<commands, each with timing and abort instructions>
```

## Escalation

| When | Who | How |
|---|---|---|
| <threshold> | <rota> | <channel/tool> |
| Suspected data loss | <name> | <phone, then #incident> |

Hand over: what you observed, what you already tried, what you have **not** tried, incident channel link.

## Appendix

- Dashboard: <link>
- Alert rules: <link>
- Logs: `<query>`
- Repo: <link> · Service doc: <link>
