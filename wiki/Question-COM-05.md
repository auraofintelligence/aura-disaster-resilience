# COM-05 How will a kiosk without internet check who is authorised to issue, change or withdraw a notice, including when a device or security key has been compromised?

[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)

## Why this matters

People need to know both who sent a notice and whether that person has the authority for that instruction.

## What to bring back

Prepare trust rules for publishers and devices: who has been given authority, when it expires, secure storage and recovery of the signing keys that prove who sent a message, withdrawing access, isolating a compromised device and handling a delayed withdrawal message. Practise what the public sees when authority is uncertain.

## What we know so far

- Straddie Disaster Kiosk Pitch.pdf — reviewed source; public copy can be added through the evidence process
- [Professional review and comparison of proposed improvements](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Professional-review) (When this work overlaps professional or public-authority responsibilities, compare the proposal and Luke's research with applicable industry/global best practice and relevant legal-engine sources. Record differences, reasonable improvements and deficiencies, with the responsible reviewer and response. Routine authorised drafting and wiki work can advance.)
- [Council plan crosswalk and proposed Aura integration](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Council-plan-crosswalk) (Relevant question row identifies the management/recovery source section and printed/PDF page. AI-generated analysis, 21 October 2026; proposed checks and actual review/operating agreements retain separate status.)

## AI-generated potential answers

**For discussion and review · research checked 2026-10-20.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

Separate transport encryption from authority to publish. Give each authorised issuer a bounded role and signing identity, with offline-verifiable records, expiry and a planned withdrawal path. Show uncertainty when the kiosk cannot confirm current authority, while retaining the issuer's original wording and source reference.

### Offline trust pack

**AI-generated adaptation of an existing pattern.** Compare a signed local issuer register with managed device credentials, protected backups and a lost-key drill. Use NIST's device-security capabilities as a review checklist; check the chosen radio firmware's authentication limits independently.

Research basis: [NIST's IoT Cybersecurity Capabilities Catalog](https://pages.nist.gov/IoT-Device-Cybersecurity-Requirement-Catalogs/) · [Meshtastic encryption](https://meshtastic.org/docs/overview/encryption/).

### Time-bounded delegated publisher

**AI-generated future concept.** Explore short-lived publication delegation for an Aura acting within a named person's or organisation's mandate. The signed record would preserve the delegator, permitted subjects, expiry and review trail, with clear public labelling of assisted drafting.

### Examples and local differences

- [Meshtastic encryption](https://meshtastic.org/docs/overview/encryption/): **AI transfer assessment:** Meshtastic's version-dependent protections show why a network label alone does not establish message trust. **Local difference to check:** Official-issuer authority and stolen-device recovery require additional local agreements and security design.

### Evidence to bring back next

- Run stolen-device, expired-authority and delayed-withdrawal exercises while offline.
- Have security reviewers compare the design with current Australian obligations and threat assumptions.

## People and connected choices

**Who reviews:** Proposed information authority and security reviewer with operator; role and appointment awaiting confirmation

**Connected questions:** [DAT-01](Question-DAT-01.md), [COM-01](Question-COM-01.md)

**Work state:** open. **Assigned person or AI assistant:** Ready to be assigned.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
