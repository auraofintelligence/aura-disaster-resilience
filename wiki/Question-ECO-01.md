# ECO-01 How will approved calendars and notices keep everyday activity, cancellations, closures and transport changes in step across kiosks?

[Start here](Home.md) · [Questions](Question-register.md) · [Progress](Progress.md) · [People decide](Human-review.md)

## Why this matters

A dated, source-backed notice gives people a useful next step during ordinary life and disruption, including while a kiosk is disconnected.

## What to bring back

Agree an exchange format with event-series and individual-date IDs, timezone, repeating-date exceptions, confirmed or awaiting-confirmation status, cancellations, postponements, source checks, approval, expiry and replacement history. Demonstrate a repeating event cancelled while a kiosk is offline and the correct update after reconnection.

## What we know so far

- [site-data.js](https://github.com/auraofintelligence/quandamooka-country-events-engine/blob/main/assets/site-data.js)
- [app.js](https://github.com/auraofintelligence/quandamooka-country-events-engine/blob/main/assets/app.js) (lines319-464)
- [SOURCE_NOTES.md](https://github.com/auraofintelligence/quandamooka-country-events-engine/blob/main/docs/SOURCE_NOTES.md)
- [PUBLIC_BOUNDARY.md](https://github.com/auraofintelligence/quandamooka-country-events-engine/blob/main/docs/PUBLIC_BOUNDARY.md)
- [Professional review and comparison of proposed improvements](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Professional-review) (When this work overlaps professional or public-authority responsibilities, compare the proposal and Luke's research with applicable industry/global best practice and relevant legal-engine sources. Record differences, reasonable improvements and deficiencies, with the responsible reviewer and response. Routine authorised drafting and wiki work can advance.)
- [Council plan crosswalk and proposed Aura integration](https://github.com/auraofintelligence/aura-disaster-resilience/wiki/Council-plan-crosswalk) (Relevant question row identifies the management/recovery source section and printed/PDF page. AI-generated analysis, 21 October 2026; proposed checks and actual review/operating agreements retain separate status.)

## AI-generated potential answers

**For discussion and review · research checked 2026-10-20.** These are AI-generated options and transfer assessments. [The user's request and research method](Research-brief.md) identify the source of this work. The [source catalogue](Research-sources.md) states what the references establish. The decision and approval record retains its own status.

Give recurring events and individual dates stable identities, with local timezone, confirmation, cancellation and replacement history. Connect the Events Engine to an approved release stream for the notice network. Offline screens would explain the saved edition and remove or qualify expired information.

### iCalendar plus a local approval record

**AI-generated adaptation of an existing pattern.** Use iCalendar identities, recurrence exceptions and revisions as a starting exchange format. Add the issuer, rights, checking time, approval scope and expiry needed by the island publishing service.

Research basis: [RFC 5545: iCalendar](https://www.rfc-editor.org/rfc/rfc5545.html).

### An Aura rehearses the effects of a changed event

**AI-generated future concept.** Explore an assistant showing an authorised organiser which linked notices, transport advice and roster entries may need review after a cancellation. It would draft updates for their actual owners and report which screens have received approved editions.

Research basis: [RFC 5545: iCalendar](https://www.rfc-editor.org/rfc/rfc5545.html) · [RFC 9171: Bundle Protocol Version 7](https://www.rfc-editor.org/rfc/rfc9171.html).

### Examples and local differences

- [RFC 5545: iCalendar](https://www.rfc-editor.org/rfc/rfc5545.html): **AI transfer assessment:** A standard calendar can identify one occurrence separately from its repeating series. **Local difference to check:** Island publishing also needs release authority, cultural permissions, expiry and evidence that disconnected screens receive cancellations.

### Evidence to bring back next

- Cancel one date in a recurring series while a kiosk is offline and verify the right occurrence after reconnection.
- Try a postponement, timezone boundary, duplicate import and organiser correction without changing unrelated dates.

## People and connected choices

**Who reviews:** Proposed calendar/notice publishing owner and organiser approval role (unconfirmed)

**Connected questions:** [DAT-01](Question-DAT-01.md), [SW-03](Question-SW-03.md)

**Work state:** open. **Assigned person or AI assistant:** Ready to be assigned.

Research and alternatives can move ahead while connected decisions develop. Before acting on a choice, check the people, evidence and approved scope in [People decide](Human-review.md).
