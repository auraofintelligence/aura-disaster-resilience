# People decide the proposal

Human-in-the-loop review means people decide the exact proposal prepared for them. AI assistants help assemble the choices, evidence, costs and checks so the decision is informed and easy to trace.

The project is at the planning and evidence-building stage. The next review milestone is a proposal with a clear purpose, a usable demonstration or check plan, and named decision roles. Initial human-review status is `none`.

Use the [Question register](Question-register.md), [Decisions](Decisions.md) and [First review](First-review.md) to find the item being considered. [Constraints](Constraints.md) preserves choices already made. [Agent work](Agent-work.md) explains preparation; [Progress](Progress.md) keeps the milestones visible; [Home](Home.md) describes the service.

## Match the decision to the person

Luke is the project initiator and will drive research, coordination and proposals forward. Where the work overlaps SES, police, fire and rescue, ambulance, Defence or other qualified professional responsibilities, his research and opinions receive review against applicable industry and international good practice and relevant legal sources. Record differences, reasonable improvements and deficiencies in the proposal or existing approach, with the evidence and the reviewer's actual assessment. [Professional review](Professional-review.md) explains the comparison method.

| Decision | Person and scope |
| --- | --- |
| Project initiation and design direction | Luke drives the proposal and chooses work within his own responsibilities, informed by participants, evidence and the relevant professional reviews. |
| Technical assessment | A suitably qualified reviewer assesses a defined question within their competence and responsibility. Record the equipment, task or installation covered. |
| Cultural or knowledge permission | The relevant custodian decides the permitted use, interpretation, audience and release conditions for their material. |
| Site or asset permission | The owner or delegated custodian decides hosting, access, installation, use and duties for that place or asset. |
| Statutory approval | The responsible public authority makes a formal decision through the applicable process. |

These roles can contribute to the same proposal while retaining their own responsibilities. For example, the user may choose a kiosk design, a site owner may agree to host it, and a qualified person may assess its electrical installation. Record the actual agreement for each relevant scope.

Choose review categories that the proposed action actually needs. Keep prospective roles “unconfirmed” until their appointment, delegation or authority is evidenced. Routine authorised drafting and local checks can continue.

## Present a choice people can assess

Explain the question ID, service outcome, options, recommendation, resources, evidence and checks. Show the next action and its limits. A photograph of the actual equipment, a short walkthrough or a worked example can make the choice clearer.

Name the proposal revision: the exact edition under review. Record its content fingerprint, also called a digest. SHA-256 is the method used to calculate that fingerprint. Record a separate fingerprint for the evidence list, which identifies the documents, photos, source versions and check results presented with the proposal.

Use the user's existing authorisation and settled decisions. If a new answer is needed, identify the material change or remaining choice. Offer a clear way to choose an option, approve a defined scope, ask for changes, defer or reject.

## Record what the person actually decided

The review record links:

- Question and decision IDs, proposal revision, content fingerprint and evidence-list fingerprint.
- The exact option, scope and next action being decided, with relevant conditions, dependent decisions and validity period.
- The reviewer's identity, role and evidence of authority for that scope.
- The actual decision and its evidence URL or authorised record reference, with date and timezone or the available date precision.
- The reasons, qualifications and follow-up the reviewer actually supplied.
- Who recorded the decision and when they checked it against the proposal.

Unknown fields remain visible so someone can resolve them. Approval is ready to support an action when the required scope, fingerprints, attributable decision, relevant authority and date are established. An incomplete approval claim remains unverified evidence.

For a private message or restricted cultural record, keep the evidence in its authorised location and publish a permitted summary and reference. This preserves a useful public trail while respecting the people involved.

## Read the review status consistently

| Status | What happened |
| --- | --- |
| `none` | A packet may be in preparation; no review request has been made. |
| `requested` | An authorised request was actually sent, with its channel and date recorded. |
| `changes_requested` | The reviewer identified changes to make. |
| `approved` | An attributable decision covers the recorded revision and scope, with its conditions and validity checked. |
| `conditional` | The person supports the proposal subject to recorded conditions; the next action awaits their completion and a fresh decision. |
| `expired` | The recorded validity period has ended and the next action needs a current decision. |
| `rejected` | The reviewer declined the recorded proposal or option. |
| `stale` | Bound content, evidence, authority or conditions have changed and need review again. |

An AI recommendation, a test result, elapsed time and a completed form have their own useful place in the record. A human decision needs the person's actual response.

## Keep approval attached to the right edition

Before using a decision, compare the current proposal, evidence fingerprints, scope, dependent decisions and conditions with the review record. If a bound element changes, retain the earlier edition and decision, mark the affected review `stale`, and present the changed edition for review.

An updated source can strengthen the same recommendation while changing its evidence. Show that change. Approval of one question covers that question's recorded scope; a dependent question retains its own decision requirements.

While a decision is pending, AI assistants can research alternatives, prepare conditional drafts and improve the evidence. The handover names the action waiting for a decision and the work that can advance now.

The dependent action stays at preparation until its required decision and permissions are recorded.

## Record the next real milestone

Keep review, checking, publication and operation as separate milestones. After an authorised action, record what happened, where, which version was used and the receipt or check result. A published planning page can help people participate while remaining a proposal.

External contact, issue posting, disclosure of private material, expenditure and deployment use the user's recorded authorisation and the relevant owner's permission for that action. Preparing a recommendation does not add that authority.

## Publish a traceable wiki

The recommended route is to review source changes in a pull request, then copy the authorised source edition into the native GitHub wiki. A pull request is a proposed change people can inspect before it joins the main source. Main and the wiki have separate Git histories: each keeps its own record of file versions.

Record the actual source edition, publication result and review status. The wiki builder checks proposal and evidence fingerprints, named GitHub reviewers, conditions and source-comment chronology. Branch protection, specialist appointments and any future automatic publishing route develop through their own recorded setup work.

For a checked GitHub approval, use the two lines shown on the decision page: the exact `HITL APPROVE` statement and `Conditions: none`. Put conditions in that field when agreement depends on something being completed; it remains conditional until the next human decision. An optional `Valid-until:` line gives an explicit date, time and timezone. Discuss reasons in another comment so the decision record stays unambiguous. [The contributor guide](../CONTRIBUTING.md) explains importing a genuine review.
