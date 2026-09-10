# Failure mode catalogue

A starter library of common failure modes, already written in the runbook format. Use these as scaffolding: keep the shape, replace the specifics with what is true of the system being documented. Delete any entry that cannot actually happen in this system - a runbook full of irrelevant entries is as bad as one with none.

Every command below is standard tooling, but the thresholds, names and expected outputs are placeholders. Verify against the real environment before marking anything verified.

## Contents

**Kubernetes:** CrashLoopBackOff, ImagePullBackOff, Pod Pending, OOMKilled, Rollout stuck
**Traffic:** 5xx spike after deploy, High latency with no errors
**Data:** Connection pool exhausted, Replica lag
**Platform:** Disk full, TLS certificate expired, In-cluster DNS failure
**Delivery:** CI pipeline suddenly failing

---

## Kubernetes

### Pods in CrashLoopBackOff

**Signal:** `KubePodCrashLooping` alert, or pods showing `CrashLoopBackOff` in triage step 1.
**Likely causes** (most common first):
1. Bad config or missing env var / secret introduced by the last deploy
2. Failing dependency at startup (DB, cache, message broker unreachable)
3. Liveness probe too aggressive for this service's startup time
4. OOMKilled on boot - see OOMKilled entry instead

**Confirm:**
```bash
kubectl -n <NAMESPACE> logs <POD> --previous --tail=50
kubectl -n <NAMESPACE> describe pod <POD> | sed -n '/Last State/,/Ready/p'
```
> The `--previous` logs show why the last attempt died - this is the important one.
> If `Reason: OOMKilled` appears, go to the OOMKilled entry.
> If the logs end mid-startup with a connection error, it's a dependency, not the app.

**Mitigate (now):** if the last deploy caused it, roll back:
```bash
kubectl -n <NAMESPACE> rollout undo deploy/<SERVICE>
```
**Blast radius:** replaces all pods; expect brief capacity reduction during the roll.

**Resolve:** fix the config or dependency, then redeploy. If the probe is the problem, raise `initialDelaySeconds` / `failureThreshold` in `<MANIFEST_PATH>` rather than removing the probe.

**Verify recovery:** pods `Running` with `RESTARTS` stable for 5 minutes.
**If this doesn't work:** the dependency is likely down - check its own runbook, then escalate to <owner>.

---

### ImagePullBackOff / ErrImagePull

**Signal:** pods stuck `ImagePullBackOff`, usually immediately after a deploy.
**Likely causes:**
1. Image tag does not exist - build failed but deploy ran anyway
2. Registry credentials expired or missing in this namespace
3. Registry unreachable (network policy, outage)

**Confirm:**
```bash
kubectl -n <NAMESPACE> describe pod <POD> | grep -A5 Events
```
> `manifest unknown` or `not found` - the tag doesn't exist, the build is the problem.
> `unauthorized` / `401` - credentials. Check the pull secret exists:
> `kubectl -n <NAMESPACE> get secret <PULL_SECRET>`

**Fix:** for a missing tag, roll back to the last good tag - do not wait for a rebuild while the service is down:
```bash
kubectl -n <NAMESPACE> rollout undo deploy/<SERVICE>
```
For credentials, re-create the pull secret per `<RUNBOOK_LINK>`.

**Verify recovery:** `kubectl -n <NAMESPACE> get pods -l app=<SERVICE>` all `Running`.
**If this doesn't work:** check whether the registry itself is up before escalating.

---

### Pods stuck in Pending

**Signal:** new pods never leave `Pending`; deploy appears to hang.
**Likely causes:**
1. No node has enough allocatable CPU/memory
2. PersistentVolumeClaim cannot bind (wrong storage class, wrong zone)
3. Node selector / affinity / taint matches nothing

**Confirm:**
```bash
kubectl -n <NAMESPACE> describe pod <POD> | tail -20
```
> The scheduler states the reason plainly: `Insufficient cpu`, `node(s) had taint`,
> or `pod has unbound immediate PersistentVolumeClaims`. Read it literally.

**Fix:** for capacity, either scale the node group or reduce the request. Confirm the pressure first:
```bash
kubectl top nodes
kubectl describe node <NODE> | grep -A6 'Allocated resources'
```
**Blast radius:** scaling nodes costs money and takes 2-5 minutes; reducing requests can cause noisy-neighbour problems later. Prefer scaling during an incident, tune requests afterwards.

**If this doesn't work:** if a PVC won't bind, check the storage class and the zone of the existing volume - a pod cannot move zones to reach its disk.

---

### OOMKilled

**Signal:** restarts climbing; `Last State: Terminated, Reason: OOMKilled`.
**Likely causes:**
1. Memory limit set below real working set
2. A genuine leak, growing over hours or days
3. A single request loading an unbounded result set

**Confirm:**
```bash
kubectl -n <NAMESPACE> describe pod <POD> | grep -A3 'Last State'
kubectl -n <NAMESPACE> top pod -l app=<SERVICE>
```
> Killed within seconds of start = limit far too low.
> Killed after hours, memory climbing steadily = leak.
> Killed under load spikes only = unbounded per-request allocation.

**Mitigate (now):** raise the limit to buy time:
```bash
kubectl -n <NAMESPACE> set resources deploy/<SERVICE> --limits=memory=<NEW_LIMIT>
```
**Blast radius:** triggers a rolling restart. Also make the same change in `<MANIFEST_PATH>`, or the next deploy silently reverts it - a very common way for an incident to recur a day later.

**Resolve:** profile the service. Raising limits forever is not a fix.
**Verify recovery:** no restarts for 30 minutes under normal load.

---

### Rollout stuck / not progressing

**Signal:** `kubectl rollout status` hangs; old and new pods both present for a long time.

**Confirm:**
```bash
kubectl -n <NAMESPACE> rollout status deploy/<SERVICE> --timeout=10s
kubectl -n <NAMESPACE> get deploy <SERVICE> -o jsonpath='{.status.conditions[*].reason}{"\n"}'
```
> `ProgressDeadlineExceeded` means new pods never became Ready. The reason is in
> the new pods, not the deployment - describe one and follow its own entry above.

**Fix:** identify why the new pods aren't Ready (readiness probe, config, image). If the cause isn't obvious within a couple of minutes, roll back and investigate with the service healthy.

**If this doesn't work:** a stuck rollout with `maxUnavailable: 0` can hold indefinitely without hurting live traffic - confirm whether users are actually affected before taking risky action.

---

## Traffic

### 5xx spike after a deploy

**Signal:** error-rate alert firing within ~15 minutes of a rollout.
**Likely causes:**
1. The new release is broken
2. A migration changed schema in a way the old pods can't handle during the roll
3. Config or secret missing in this environment only

**Confirm:**
```bash
kubectl -n <NAMESPACE> rollout history deploy/<SERVICE> | tail -3
kubectl -n <NAMESPACE> logs -l app=<SERVICE> --since=15m | grep -iE 'error|exception' | head -30
```
> Correlate the error onset with the rollout timestamp. If errors began *before*
> the deploy, the deploy is a coincidence - go to the dependency checks instead.

**Mitigate (now):**
```bash
kubectl -n <NAMESPACE> rollout undo deploy/<SERVICE>
```
> **Do not roll back** if the release ran a forward-incompatible migration.
> Check `<MIGRATIONS_TABLE>` first. If one ran, escalate to <owner> - rolling
> back into a migrated database can corrupt data.

**Verify recovery:** error rate back under `<THRESHOLD>` for 10 minutes.
**Resolve:** reproduce in staging before re-releasing.

---

### High latency, no errors

**Signal:** p99 latency alert, error rate normal.
**Likely causes:**
1. A slow downstream dependency (DB, upstream API) that is timing out slowly rather than failing
2. Connection pool saturation - requests queue instead of erroring
3. Under-provisioned replicas for current traffic
4. A slow query introduced by a recent change

**Confirm:**
```bash
kubectl -n <NAMESPACE> top pod -l app=<SERVICE>
```
> CPU pegged near limit = capacity or a hot code path. CPU low but latency high
> = the service is waiting on something else. That distinction decides everything
> that follows.

For waiting: check the slowest dependency in `<DASHBOARD_LINK>` and go to its runbook.
For capacity:
```bash
kubectl -n <NAMESPACE> scale deploy/<SERVICE> --replicas=<N>
```
**Blast radius:** more replicas means more DB connections. Confirm headroom before scaling, or you convert a latency incident into a pool exhaustion incident.

---

## Data

### Database connection pool exhausted

**Signal:** `too many connections`, `pool timeout`, or requests hanging then timing out.
**Likely causes:**
1. Service scaled up; replicas x pool size now exceeds the server limit
2. Connection leak - connections not returned on an error path
3. Long-running queries holding connections

**Confirm (Postgres):**
```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
SHOW max_connections;
```
> `idle in transaction` in quantity means a leak - the app opened a transaction
> and never closed it. `active` in quantity means slow queries, not a leak.

**Mitigate (now):** terminate long-idle transactions:
```sql
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle in transaction' AND state_change < now() - interval '10 minutes';
```
> **Destructive.** This aborts those transactions. Safe for idle ones, but confirm
> no batch job is legitimately running long before you run it.

**Resolve:** fix the leak, or move to a pooler (PgBouncer) rather than raising `max_connections` indefinitely - each connection costs real memory on the DB server.

---

### Replica lag

**Signal:** users see stale data; read-replica lag alert.
**Confirm (Postgres):**
```sql
SELECT now() - pg_last_xact_replay_timestamp() AS lag;
```
> Compare against `<ACCEPTABLE_LAG>`. Lag that grows steadily is different from
> lag that spiked and is recovering - the second usually needs no action.

**Mitigate:** route reads to the primary temporarily if the application supports it (`<HOW>`), accepting the extra primary load.
**Resolve:** find the cause - usually a large write batch, a long-running query blocking replay, or replica resource starvation.

---

## Platform

### Disk full

**Signal:** `DiskPressure` on a node, writes failing, or pods evicted.
**Likely causes:**
1. Log growth without rotation
2. Container image accumulation on the node
3. A PVC genuinely full

**Confirm:**
```bash
kubectl get nodes -o wide
kubectl describe node <NODE> | grep -A5 Conditions
df -h            # on the node, if you have access
```

**Mitigate (now):** reclaim image space on the node:
```bash
crictl rmi --prune
```
> **Check first** that this node isn't about to need those images for a rollout.

For a full PVC, expand it if the storage class allows:
```bash
kubectl -n <NAMESPACE> patch pvc <PVC> -p '{"spec":{"resources":{"requests":{"storage":"<SIZE>"}}}}'
```
> Expansion is one-way. You cannot shrink it back.

**Resolve:** fix log rotation or retention. Disk-full incidents always recur if only the symptom is cleared.

---

### TLS certificate expired

**Signal:** clients report certificate errors; browsers refuse the site. Usually total and sudden.
**Confirm:**
```bash
echo | openssl s_client -connect <HOST>:443 -servername <HOST> 2>/dev/null \
  | openssl x509 -noout -dates -subject
```
> `notAfter` in the past confirms it. Also check you're hitting the right endpoint -
> an expired cert on a load balancer and on an origin need different fixes.

**Fix (cert-manager):**
```bash
kubectl -n <NAMESPACE> get certificate
kubectl -n <NAMESPACE> describe certificate <CERT>
```
> The `Ready` condition explains the failure - usually a failed ACME challenge
> (DNS record missing, or rate-limited by the CA). The renewal has typically been
> failing silently for days; the expiry is just when it became visible.

**Resolve:** fix the renewal cause and add an alert at 21 days before expiry. An expiry incident means monitoring failed, not just the cert.

---

### In-cluster DNS resolution failing

**Signal:** intermittent `no such host` / `EAI_AGAIN` errors across multiple services.
**Confirm:**
```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl -n <NAMESPACE> exec -it <POD> -- nslookup <SERVICE>.<NAMESPACE>.svc.cluster.local
```
> Failures across several unrelated services point at cluster DNS. Failures in one
> service point at that service's config.

**Mitigate:** restart the DNS deployment:
```bash
kubectl -n kube-system rollout restart deploy/coredns
```
**Blast radius:** brief resolution failures cluster-wide during the roll. Do this deliberately, not reflexively.
**Resolve:** check CoreDNS logs and CPU limits - throttling under load is a common cause of intermittent failures.

---

## Delivery

### CI pipeline suddenly failing with no code change

**Signal:** builds that passed yesterday fail today on the same commit.
**Likely causes:**
1. An expired token, credential, or registry login
2. A floating dependency or base-image tag that moved
3. Runner out of disk or a poisoned cache
4. An upstream service the build depends on being down

**Confirm:** read the first error in the log, not the last - later failures are usually cascades. Then:
```bash
# does it fail the same way on a clean cache / fresh runner?
```
> Passing on a clean runner and failing on the shared one means cache or disk.
> Failing everywhere on an unchanged commit means an external dependency moved.

**Fix:** clear the cache, rotate the credential, or pin the dependency that moved.
**Resolve:** pin base images and toolchain versions by digest. "It worked yesterday" is a symptom of unpinned inputs, and it will happen again.
