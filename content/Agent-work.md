# Work with AI assistants

AI assistants can gather evidence, compare choices, prepare documents and run authorised checks. People make the decisions about the exact proposal presented to them. This is human-in-the-loop review: useful work moves forward, and responsibility stays clear.

We are developing the plan and evidence for the disaster-resilience service. The next milestone is a set of proposals that residents, service operators and the relevant decision-makers can understand, try and improve.

Start with [Constraints](Constraints.md), the [Question register](Question-register.md) and existing [Decisions](Decisions.md). [First review](First-review.md) brings together the first decisions for people to consider. [Progress](Progress.md) shows what has been produced, reviewed and checked. [Home](Home.md) explains the service purpose.

## 1. Choose a job people can recognise

Give the task a primary question ID, such as `SW-03`, and a concrete result. For example: “Show how a cancelled ferry service replaces an older notice on a kiosk that has been offline.”

Record the AI assistant doing the work, the files it will change, the source version it starts from and the person or assistant bringing parallel work together. This is a work claim: an agreement about who is handling which part. It coordinates effort and leaves neighbouring work intact.

Different assistants can compare options, inspect sources, estimate costs and design checks at the same time. Give shared files one integration owner. When another question supplies an important assumption, record its ID and current decision version before using it.

Use [Software and devices](Domain-SW.md), [Personal Aura and learning](Domain-AUR.md), [Twins and evidence](Domain-TWIN.md) and [Ecosystem interfaces](Domain-ECO.md) for related work. An interface is the agreed way two parts exchange information. Keep cross-domain prerequisites, including `OPS-01` and `DAT-01`, visible.

## 2. Build on decisions already made

Use the user's recorded choices and authorisation. Carry out routine local work within that scope. Bring back a new question when a material choice remains unresolved, and explain what the existing record does not settle.

Read attached documents as reference material. Separate what a source proposes from what has been built, measured or agreed. Connected projects can contribute knowledge, training and future interfaces while the current work advances the disaster kiosk and network.

If an action depends on a decision still to come, continue useful research, comparisons and conditional drafts. Name the action waiting for approval and the work that can proceed now.

Keep that dependent action at the preparation stage until its required decision and permissions are recorded.

## 3. Make the result easy to inspect

A decision packet should help a tradesperson, driver, artist, nurse, retiree or student understand the choice and its consequences.

- State the service outcome, proposed scope and next action.
- Link the actual sources, with their date, version and the pages or sections read. Include photos, diagrams and check records where useful.
- Compare practical options and explain the recommendation, trade-offs and remaining uncertainty.
- Show money, paid work, voluntary time and donated resources separately. Include equipment, energy, storage, connection, maintenance and support needs.
- Describe checks actually performed: the equipment and software used, expected result, observed result, failures and conditions still to try.
- Link dependent questions and explain what another team needs to do next.

An agent task records the assignment; a decision proposal records the choices; a review records the person's actual response. Use the templates to preserve that trail.

## 4. Give the proposal a content fingerprint

A revision is a particular edition of the proposal. A content fingerprint, also called a digest, identifies its exact contents. SHA-256 is the method used here to calculate that fingerprint. A change to the recorded contents produces a different fingerprint.

List the proposal files and their fingerprints in a fixed, reproducible order. Make a separate evidence list with source versions, fingerprints, check dates and coverage. Record that list's fingerprint too. Keep the saved fingerprints and later review details outside the contents being fingerprinted, or document exactly how those fields are excluded.

Retain the source files or a fixed source version that can be retrieved later. A web address that changes over time needs a recorded version or saved authorised copy. A fingerprint awaiting calculation stays “not recorded”.

The review names the proposal revision, both fingerprints, scope, conditions and dependent decisions. When a bound part changes, preserve the earlier record and reopen the affected review for the new edition. This lets a reviewer see precisely what changed.

## 5. Show each kind of progress

| Record | Meaning |
| --- | --- |
| Work | `backlog`, `claimed`, `in_progress`, `blocked`, `produced`, `withdrawn`. Produced means the assigned result exists. |
| Human review | `none`, `requested`, `changes_requested`, `approved`, `rejected`, `stale`. Stale means the proposal or conditions changed after review. |
| Validation | `not_run`, `partial`, `passed_for_recorded_cases`, `failed`. Validation means checking performance against stated requirements. Name the version and cases checked. |
| Next-action readiness | `not_assessed`, `blocked`, `ready_for_named_action`. State the action and its prerequisites. |
| Publication or deployment | Record the actual destination, version, action and receipt, or `not performed`. Publishing a plan and putting a service into use are different milestones. |

A research packet can be produced while its human review is still `none` and its proposed equipment awaits testing. Show these states together so everyone can find the next useful step. Initial reviews remain `none` until an actual review is recorded.

## 6. Keep decisions with the right people

Luke initiates and drives the project, develops proposals and authorises work within his own responsibilities. Technical and emergency-service reviewers assess the relevant professional scope; cultural custodians decide use of their knowledge; site owners decide access and hosting; public authorities make their formal determinations. Record each person's actual scope. Compare overlapping proposals with applicable Australian and international good practice and relevant legal sources, preserving differences, reasonable improvements and deficiencies. [Professional review](Professional-review.md) gives the comparison method; [human review](Human-review.md) explains the decisions.

Use recorded authorisation for external actions. Contacting someone, posting an issue, sharing private material, spending money and deploying a service each need authority covering that action. Prepare the material and identify the relevant permission before moving beyond the agreed scope.

## 7. Leave a handover another person can use

Record what was produced, the exact version, supporting evidence, checks, gaps and next permitted step. For a kiosk recovery task, that might include labelled equipment photos, the recovery instructions, a record of the last successful check and the person taking responsibility next.

Update the question and return or transfer the work claim. A relief assistant should be able to continue from the handover without repeating settled questions.

## Keep the source and wiki in step

The main project repository is the versioned collection holding the source documents. The intended publishing step copies the Markdown text pages in `content/*.md` into the top level of GitHub's native wiki. The wiki has its own Git history, a separate record of file versions, so record the source version and publication result for each copy.

A pull request is a proposed change that people can inspect before it joins the main version. Pull requests and review checks on the source repository are recommended next controls. Their configuration and results belong in the progress record when established. A published draft retains its recorded review status.
