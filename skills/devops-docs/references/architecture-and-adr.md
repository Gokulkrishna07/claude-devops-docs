# Architecture docs and ADRs

Two different jobs. Architecture docs describe how the system is shaped now. ADRs record why it got that way. Both fail in the same manner: they describe the obvious and omit the reasoning that would actually help someone.

## Architecture documents

**One diagram, and it must be accurate.** A wrong diagram is worse than none - people plan against it. Prefer a text-based format (Mermaid, D2) checked into the repo so it can be reviewed alongside code. Diagrams in Figma or a screenshot go stale invisibly.

Show what carries risk: request flow, data flow, trust boundaries, where state lives, where the single points of failure are. Not every component - a diagram with 40 boxes communicates nothing.

Then, in prose:

- **How a request actually flows.** Follow one real request end to end, naming every hop.
- **Where state lives**, and which store is the source of truth when several hold the same data.
- **Trust and network boundaries.** What's public, what's internal, where authentication happens.
- **The known weak points.** Every system has them. Writing them down is a sign of maturity, and it is the section a new engineer most needs. Omitting them doesn't hide them, it just means they get discovered during an incident.
- **Scaling limits.** What breaks first under 10x load, and roughly at what point.

Skip: technology descriptions, aspirational future-state mixed in with current state (label it clearly if included), and any diagram nobody will update.

## Architecture Decision Records

One decision per file, immutable once accepted. Superseded decisions get a new ADR that links back rather than an edit - the history is the value.

    # ADR-<NNN>: <decision in a short imperative phrase>

    **Status:** Proposed | Accepted | Superseded by ADR-<NNN>
    **Date:** <YYYY-MM-DD>
    **Deciders:** <names>

    ## Context
    What forced a decision. Constraints, deadlines, team size, cost limits,
    existing commitments. Be honest about the real drivers - "we had three weeks
    and one engineer who knew Postgres" is far more useful to a future reader
    than a tidied-up rationalisation.

    ## Decision
    What was decided, stated plainly.

    ## Alternatives considered
    What else was on the table and why it lost. This is the section that stops
    the same debate being reopened every six months.

    ## Consequences
    What this makes easy, what it makes hard, what it locks in, what it costs.
    Include the negatives - an ADR with only upsides was written to justify a
    decision, not to record one.

Write the ADR when the decision is made, not later. Reconstructed reasoning is invention.
