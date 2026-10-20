# Human review record: <review ID>

People decide the exact proposal presented to them. This is the human-in-the-loop step: the AI assistant prepares the choices and evidence; the relevant person supplies the decision.

Initial human-review status is `none`. Complete the record with attributable facts as each step happens.

## Proposal presented

| Field | Record |
| --- | --- |
| Review ID | Not assigned |
| Decision and question IDs | Not assigned |
| Proposal revision | Not recorded |
| Main source version | Not recorded |
| Exact scope and next action | Not recorded |
| Proposal contents and SHA-256 fingerprint | Not recorded |
| Evidence-list version and SHA-256 fingerprint | Not recorded |
| Fingerprint method and verification date | Not recorded |
| Dependent decisions and versions | Not recorded |
| Work reserved for another decision | Not recorded |
| Current work status | `backlog` |
| Current human-review status | `none` |
| Current check status | `not_run` |
| Next-action readiness | `not_assessed` |

A revision is a particular edition. A content fingerprint, also called a digest, identifies its exact contents; SHA-256 is the calculation method. The evidence list names the versions of documents, photos and check results presented with it.

## Person and responsibility

- Decision type needed:
- Reviewer's identity: Unconfirmed.
- Relevant competence, custodianship, ownership, office or delegated role: Unconfirmed.
- Evidence of authority for this scope: Not recorded.
- Other people whose distinct permission is needed: Awaiting assessment.
- User choices and authorisation already covering this work:

For example, a user can choose a preferred design, a site owner can agree to host it, and a qualified person can assess the installation. Record their respective scopes. [Constraints](Constraints.md) and [Human review](Human-review.md) help preserve settled choices and the remaining decisions.

## Packet and request

- Location and exact edition presented:
- Options, recommendation and useful comparison:
- Costs, equipment, people, assumptions and uncertainty:
- Checks completed, failures and conditions still to try:
- Requested decision and proposed conditions:
- Existing authorisation to contact this person, where needed: Not recorded here.
- Actual request channel, evidence reference and sent date/timezone: Not sent.

Use the recorded authorisation for contact, posting and information sharing. Preparing this packet is local work; sending it is a separate action with its own scope and record. Status becomes `requested` when an authorised request is actually sent.

## Actual response

| Field | Record |
| --- | --- |
| Human decision | No decision recorded |
| Disposition | `none` |
| Exact option and scope accepted or declined | Not recorded |
| Reviewer's identity and decision role | Unconfirmed |
| Attributable response URL or authorised record reference | Not recorded |
| Actual decision date/timezone or available date precision | Not recorded |
| Reasons and qualifications actually supplied | Not recorded |
| Conditions, reserved matters and validity period | Not recorded |
| Remaining permissions or decisions | Unresolved |
| Recorded by and checked at | Not recorded |
| Permitted public summary and handling of restricted evidence | Awaiting assessment |

Available review states are `none`, `requested`, `changes_requested`, `approved`, `rejected` and `stale`. Stale means bound contents or conditions changed after the review.

Use the person's actual response for identity, date, reasons and decision evidence. Unknown information stays marked for follow-up. Keep private messages and restricted cultural or personal material in their authorised location, with a permitted public summary.

Approval supports an action when its required scope, fingerprints, attributable decision, relevant authority and date are established. An incomplete approval claim remains unverified evidence. An AI recommendation, elapsed time or a successful check belongs in its own record rather than standing in for the person's response.

## Check that the decision still fits

| Bound item | Value reviewed | Current value and evidence | Match, changed or unresolved |
| --- | --- | --- | --- |
| Proposal revision, scope and fingerprint | Not recorded | Awaiting check | Unresolved |
| Evidence list and fingerprint | Not recorded | Awaiting check | Unresolved |
| Dependent decisions | Not recorded | Awaiting check | Unresolved |
| Conditions, authority and validity | Not recorded | Awaiting check | Unresolved |

When a bound item changes, retain this review, mark the affected approval `stale` and review the changed edition. Approval of a prerequisite covers its recorded scope; the dependent action keeps its own requirements.

## Next milestone and handover

- Exact action covered by this decision: None recorded.
- User authorisation and other permissions for that action: Not established here.
- Actions awaiting a decision and their prerequisites:
- Research or local preparation that can advance:
- Labelled photos, instructions and checks useful to the next person:
- Actual publication, deployment, contact, purchase or test and receipt: Not performed.
- Replacement or next review ID: None recorded.
- Question and dependency records to update:

Keep [Progress](Progress.md), the [Question register](Question-register.md) and [Decisions](Decisions.md) in step. Publishing a draft is a useful participation milestone; its review status and the readiness of the service remain separately recorded.
