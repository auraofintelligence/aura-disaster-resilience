# SW-04 How will authorised staff sign in, hand over responsibility and recover access after a device or access key is lost?

[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)

## Why this matters

Relief staff need usable access during long outages, while the service needs a clear record of who can publish, maintain equipment or handle private requests.

## What to bring back

Map likely misuse and failure cases, then set out staff roles and device keys from first setup through replacement. Explain offline sign-in, relief access, withdrawal of access and recovery. Check a stolen device, an expired permission, a withdrawn publisher key and an absent administrator against DAT-01.

## What we know so far

- comprehensive rebuild plan — reviewed source; public copy can be added through the evidence process
- [Aura_Genesis_Protocol_Game_Design_Document_V2.pdf](https://github.com/auraofintelligence/aura-genesis-geode-atlas/blob/main/documents/Aura_Genesis_Protocol_Game_Design_Document_V2.pdf) (pp.27,37)
- [Aura_Teacher_Training_60_Days.pdf](https://github.com/auraofintelligence/aura-genesis-geode-atlas/blob/main/documents/Aura_Teacher_Training_60_Days.pdf) (p.42)
- [Professional review and comparison of proposed improvements](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Professional-review) (When this work overlaps professional or public-authority responsibilities, compare the proposal and Luke's research with applicable industry/global best practice and relevant legal-engine sources. Record differences, reasonable improvements and deficiencies, with the responsible reviewer and response. Routine authorised drafting and wiki work can advance.)

## AI-generated potential answers

**For discussion and review · research checked 2026-10-20.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

Give staff named roles and individual access, with a practical backup and recorded shift handover. Prepare lost-device and absent-administrator recovery before deployment. Set explicit limits for offline permissions and explain when a disconnected kiosk has yet to receive an access withdrawal.

### Named access with rehearsed recovery

**AI-generated adaptation of an existing pattern.** Compare suitable staff authenticators and recovery arrangements using NIST's event-management guidance. Keep public browsing available as a guest, and rehearse qualified staff replacing a lost credential without exposing another person's account.

Research basis: [NIST SP 800-63B-4: authenticator event management](https://pages.nist.gov/800-63-4/sp800-63b/events/).

### Short-lived delegated shift credentials

**AI-generated future concept.** Explore a narrowly scoped temporary credential for an agreed relief shift, with a visible expiry and an independent recovery holder. Test clock uncertainty and delayed withdrawals before accepting it for sensitive actions.

Research basis: [NIST SP 800-63B-4: authenticator event management](https://pages.nist.gov/800-63-4/sp800-63b/events/).

### Examples and local differences

- [NIST SP 800-63B-4: authenticator event management](https://pages.nist.gov/800-63-4/sp800-63b/events/): **AI transfer assessment:** Access includes replacement, invalidation and recovery throughout an authenticator's life. **Local difference to check:** An island outage introduces delayed revocation information and a smaller roster of available, authorised relief staff.

### Evidence to bring back next

- Rehearse a stolen staff device, an expired permission and a withdrawn publishing credential during internet loss.
- Agree who actually holds recovery responsibility, its limits and the review required for sensitive actions.

## People and connected choices

**Who reviews:** Proposed security lead and delegated service owner (unconfirmed)

**Connected questions:** [DAT-01](Question-DAT-01.md), [SW-03](Question-SW-03.md)

**Work state:** open. **Assigned person or AI assistant:** Ready to be assigned.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
