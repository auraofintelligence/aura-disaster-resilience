# COM-04 What will each connection carry, and how will records wait, retry and combine after an outage while keeping different reports visible?

[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)

## Why this matters

A network can combine stored records while people still need to check two reports that disagree about the real world.

## What to bring back

Specify record sizes, priorities, waiting-message capacity, retry and receipt rules, duplicate checks, checks for altered records, retention and portable import/export. Walk through a split network reconnecting, including one report saying a road is blocked and another saying it is clear.

## What we know so far

- Straddie Disaster Kiosk Pitch.pdf — reviewed source; public copy can be added through the evidence process
- GPT Straddie Disaster Kiosks.pdf — reviewed source; public copy can be added through the evidence process
- [Professional review and comparison of proposed improvements](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Professional-review) (When this work overlaps professional or public-authority responsibilities, compare the proposal and Luke's research with applicable industry/global best practice and relevant legal-engine sources. Record differences, reasonable improvements and deficiencies, with the responsible reviewer and response. Routine authorised drafting and wiki work can advance.)

## AI-generated potential answers

**For discussion and review · research checked 2026-10-20.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

Use durable queues with stable record identities, visible issue times and explicit update or cancellation references. Reconnection should preserve conflicting observations for review rather than silently replacing one. Compare retry schedules and transport sizes while protecting essential traffic from media or bulk sensor uploads.

### Versioned local queue

**AI-generated adaptation of an existing pattern.** Keep the durable queue in the kiosk application and use CAP-style alert references where applicable. Treat any low-power mesh as a constrained transport whose capacity, persistence and authentication are separately tested on pinned firmware.

Research basis: [Common Alerting Protocol Version 1.2](https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html) · [Meshtastic encryption](https://meshtastic.org/docs/overview/encryption/).

### Meaning-preserving transfer planner

**AI-generated future concept.** Develop an Aura-assisted planner that sends essential structured records first and requests rich supporting material later. It could highlight contradictory road observations with their sources and dates while an authorised person decides the public update.

### Examples and local differences

- [Common Alerting Protocol Version 1.2](https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html): **AI transfer assessment:** CAP provides explicit identities and references for changed or cancelled alert messages. **Local difference to check:** Request queues, observation conflicts, receipts and disconnected storage need additional application rules.

### Evidence to bring back next

- Reconnect two simulated settlements with duplicate, expired and contradictory records.
- Measure backlog growth and recovery time across the slowest candidate link.

## People and connected choices

**Who reviews:** Proposed distributed-systems lead with data and operations reviewers; role and appointment awaiting confirmation

**Connected questions:** [DAT-01](Question-DAT-01.md), [COM-01](Question-COM-01.md), [COM-02](Question-COM-02.md)

**Work state:** open. **Assigned person or AI assistant:** Ready to be assigned.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
