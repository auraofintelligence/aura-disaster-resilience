# ENE-06 How will the kiosk start again after a flat battery, damaged stored data, repeated voltage drops or loss of a reliable clock?

[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)

## Why this matters

A planned restart restores useful information and lets people see when the time or freshness of a notice needs checking.

## What to bring back

Write and practise the restart sequence. Check stored records, show a clear status during recovery, explain uncertain time, protect queued messages and test repeated power interruptions. A brownout is a drop in supply voltage; black start means starting after all normal power has been lost.

## What we know so far

- Straddie Disaster Kiosk Pitch.pdf — reviewed source; public copy can be added through the evidence process
- [Professional review and comparison of proposed improvements](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Professional-review) (When this work overlaps professional or public-authority responsibilities, compare the proposal and Luke's research with applicable industry/global best practice and relevant legal-engine sources. Record differences, reasonable improvements and deficiencies, with the responsible reviewer and response. Routine authorised drafting and wiki work can advance.)

## AI-generated potential answers

**For discussion and review · research checked 2026-10-20.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

Give the kiosk a recovery path that starts essential information first, checks stored records and then enables larger services. Preserve queued messages across repeated power interruptions, identify uncertain time clearly and compare a known-good recovery image with a replaceable preconfigured computer module.

### Known-good startup and spare

**AI-generated adaptation of an existing pattern.** Prototype supported boot watchdog and alternate-image recovery, with protected configuration backups and a tested spare. Check voltage stability and local storage recovery before interpreting a successful reboot as successful service restoration.

Research basis: [Raspberry Pi EEPROM bootloader documentation](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/eeprom-bootloader.adoc) · [NIST's IoT Cybersecurity Capabilities Catalog](https://pages.nist.gov/IoT-Device-Cybersecurity-Requirement-Catalogs/).

### Self-checking recovery twin

**AI-generated future concept.** Develop an independent low-power supervisor that compares expected startup stages with observed health. An Aura could explain the fault and propose the next permitted check while the supervisor controls a bounded restart policy.

### Examples and local differences

- [Mallacoota Area Grid Storage community updates](https://www.ausnetservices.com.au/projects-and-innovation/completed-projects/mallacoota-area-grid-storage-mags-community-update): **AI transfer assessment:** Mallacoota's updates distinguish equipment availability from successful automatic and remote startup. **Local difference to check:** Kiosk startup also requires intact records, trustworthy status and a usable public interface.

### Evidence to bring back next

- Inject repeated brownouts and incomplete writes in a controlled bench exercise.
- Reconcile message queues and uncertain clocks before reconnecting simulated sites.

## People and connected choices

**Who reviews:** Proposed embedded reliability lead with authorised publisher role; role and appointment awaiting confirmation

**Connected questions:** [DAT-01](Question-DAT-01.md), [ENE-04](Question-ENE-04.md), [ENE-05](Question-ENE-05.md), [COM-04](Question-COM-04.md)

**Work state:** open. **Assigned person or AI assistant:** Ready to be assigned.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
