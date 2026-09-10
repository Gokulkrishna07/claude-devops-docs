# Payments Service Runbook

Last verified: 2026-01-15 by @jane

## Symptom: 5xx rate above 5% on `payments-api`

1. Check recent deploys: `kubectl rollout history deployment/payments-api -n payments`
   Expected output: a numbered revision list. If the top revision is < 10 minutes old, suspect the deploy.
2. Roll back: `kubectl rollout undo deployment/payments-api -n payments`
   Blast radius: restarts all 6 replicas over ~40s; expect a brief spike in 502s during the restart.

Escalate to @jane (primary) or #payments-oncall if unresolved after 15 minutes.

## Cost

NAT gateway data processing for this VPC: $46.12/month as of 2026-01-10, from the AWS Cost Explorer export (see `docs/cost/nat-gateway.csv`).
