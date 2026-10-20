# ENE-01 How much power does every part use when starting, waiting, working and communicating, and how does that change through the day?

[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)

## Why this matters

Measuring the whole system lets us plan both demanding simulations and the essential service during an outage.

## What to bring back

Make a device-by-device power sheet and daily energy budget. Include screens at different brightness, radio bursts, storage, cooling and energy lost in conversion. Record peak demand, measurement method and uncertainty; compare essential-service and intensive-computing schedules.

## What we know so far

- Straddie Disaster Kiosk Pitch.pdf — reviewed source; public copy can be added through the evidence process
- [Professional review and comparison of proposed improvements](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Professional-review) (When this work overlaps professional or public-authority responsibilities, compare the proposal and Luke's research with applicable industry/global best practice and relevant legal-engine sources. Record differences, reasonable improvements and deficiencies, with the responsible reviewer and response. Routine authorised drafting and wiki work can advance.)

## AI-generated potential answers

**For discussion and review · research checked 2026-10-20.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

Start with a measured energy ledger for each device and operating state. Record startup peaks separately from daily watt-hours, including display brightness, radio transmission, cooling and conversion losses. Compare always-on rich service with an essential local service plus scheduled larger jobs.

### Metered operating profiles

**AI-generated adaptation of an existing pattern.** Compare shunt-based DC measurement and a suitable AC meter, checking both against a reference. Include a Starlink Mini only as a candidate uplink: its published 25–40 W average needs confirmation on the actual unit.

Research basis: [Cerbo GX manual: configuration](https://www.victronenergy.com/media/pg/Cerbo_GX/en/configuration.html) · [Starlink Mini specification sheet, pages 3 and 8](https://www.starlink.com/public-files/specification_sheet_mini.pdf).

### Energy-aware Aura scheduler

**AI-generated future concept.** Give each AI, XR and robotics job an estimated energy allowance and measured completion record. A local scheduler could offer a lower-energy route or defer work while reserving power for public information and request handling.

### Examples and local differences

- [Finding new energy solutions for the town of Kalbarri](https://www.westernpower.com.au/resources-education/network-improvements/network-upgrade-projects/kalbarri-microgrid/): **AI transfer assessment:** Kalbarri links local supply with community demand adjustment during islanded operation. **Local difference to check:** Kiosk priorities and actual device energy need finer measurement than a town-scale comparison provides.

### Evidence to bring back next

- Measure startup, idle, busy and failed-network states on actual devices.
- Publish watt-hours per day with sampling method, uncertainty and service assumptions.

## People and connected choices

**Who reviews:** Proposed power designer with software and communications leads; role and appointment awaiting confirmation

**Connected questions:** [OPS-01](Question-OPS-01.md), [PHY-01](Question-PHY-01.md), [COM-01](Question-COM-01.md)

**Work state:** open. **Assigned person or AI assistant:** Ready to be assigned.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
