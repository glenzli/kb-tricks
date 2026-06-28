---
name: cycle-postmortem
description: "Analyze incidents with root cause, timeline, blast radius, defense gaps, action items, and optional KB fault propagation."
---

# Cycle Postmortem

Use after an outage, production incident, severe regression, or near miss.

## Hard Rules

- Separate facts, evidence, and inference.
- Do not invent logs, timestamps, customer impact, or root causes.
- Treat source, configs, telemetry, tickets, and maintained docs as authority.
- Use KB only for routing or fault propagation when fresh.

## Inputs

Collect what exists:

- Incident summary.
- Timeline.
- Logs, stack traces, alerts, dashboards, tickets.
- Deployed version or commit range.
- Mitigation already applied.

## Analysis

Cover these dimensions:

- Root cause: include 5 Whys when evidence supports it.
- Blast radius: users, requests, data, SLA, downstream systems.
- Timeline: start, detection, escalation, mitigation, recovery.
- Defense gaps: monitoring, tests, review, rollout, rollback, ownership.
- Systemic fixes: immediate, short-term, long-term.
- Optional KB propagation: source path -> fresh KB doc -> dependent modules.

## Output

Produce a postmortem report:

- Incident summary.
- Timeline.
- Root cause and trigger.
- Blast radius.
- Defense gaps.
- Fault propagation diagram if useful.
- Action items with priority, owner suggestion, and verification path.
- Follow-ups: `review-code`, `review-test`, `kb-update`, `cycle-changelog` when relevant.

