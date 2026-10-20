# SW-02 How will messages and requests move between kiosks, portable devices and connection points as links fail and return?

[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)

## Why this matters

A message may need to wait on a device before moving on. People should see whether it is waiting, delivered or acknowledged by the receiving person.

## What to bring back

Define a message package that can use different connection methods. Work through retries, duplicates, ordering, expiry, priorities and storage limits. Demonstrate disconnection and reconnection, with separate records for waiting, delivery, rejection and acknowledgement. Measure performance against OPS-01.

## What we know so far

- comprehensive rebuild plan — reviewed source; public copy can be added through the evidence process
- [Web3_Sensorium_for_Science_Debate.pdf](https://github.com/auraofintelligence/aura-verse-box/blob/main/documents/Web3_Sensorium_for_Science_Debate.pdf) (pp.5-9)
- [Aura_Teacher_Training_60_Days.pdf](https://github.com/auraofintelligence/aura-genesis-geode-atlas/blob/main/documents/Aura_Teacher_Training_60_Days.pdf) (pp.42,55)
- [Professional review and comparison of proposed improvements](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Professional-review) (When this work overlaps professional or public-authority responsibilities, compare the proposal and Luke's research with applicable industry/global best practice and relevant legal-engine sources. Record differences, reasonable improvements and deficiencies, with the responsible reviewer and response. Routine authorised drafting and wiki work can advance.)

## AI-generated potential answers

**For discussion and review · research checked 2026-10-20.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

Give each message an identity, origin, edition, priority, expiry and receipt history. Save it before transmission, retry without multiplying requests, and show waiting, delivered and accepted as different states. Compare a straightforward queue with delay-tolerant networking against the same outage cases.

### Compare ordinary queues with Bundle Protocol

**AI-generated adaptation of an existing pattern.** Trial a simple persistent queue alongside a compatible Bundle Protocol implementation. Send the same small notices over intermittent links and compare lost messages, duplicates, storage, operator effort and acknowledgement meanings.

Research basis: [RFC 9171: Bundle Protocol Version 7](https://www.rfc-editor.org/rfc/rfc9171.html) · [ODK Collect: managing draft, ready-to-send and sent forms](https://docs.getodk.org/collect-forms/).

### Approved carry-and-sync journeys

**AI-generated future concept.** Explore a portable device carrying authorised message bundles between separated hubs. A later robot or vehicle could perform that journey once capability, access, energy and responsibility are demonstrated; it would retain the same expiry and receipt rules.

Research basis: [RFC 9171: Bundle Protocol Version 7](https://www.rfc-editor.org/rfc/rfc9171.html) · [Robots to the rescue in hazardous environments](https://www.csiro.au/en/news/all/articles/2021/december/robots-to-the-rescue-in-hazardous-environments).

### Examples and local differences

- [RFC 9171: Bundle Protocol Version 7](https://www.rfc-editor.org/rfc/rfc9171.html): **AI transfer assessment:** Delay-tolerant protocols allow sender and receiver to connect at different times. **Local difference to check:** Island routes, data permissions, storage budgets and receiving-service acceptance remain local engineering and operating work.

### Evidence to bring back next

- Reorder and duplicate messages, break a transfer, fill storage and reconnect two isolated groups.
- Measure completion time and prove that network delivery cannot be mistaken for an operator accepting a request.

## People and connected choices

**Who reviews:** Proposed network software lead and duty operations lead (unconfirmed)

**Connected questions:** [SW-01](Question-SW-01.md), [DAT-01](Question-DAT-01.md)

**Work state:** open. **Assigned person or AI assistant:** Ready to be assigned.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
