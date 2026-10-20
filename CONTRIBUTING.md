# Bring useful work into the shared workshop

Start with a question in the [wiki](wiki/Question-register.md). Its card explains the purpose, starting evidence, connected questions, expected work and review route. A photo with permission, a measured drawing, a demonstration or a practical explanation can all move the design forward.

## Update a question

Edit its record in `data/questions.json`. Keep its ID. Record who is doing the work, what has been produced, source links and the current work state. Put a longer explanation in `content/` or a versioned evidence file under `docs/`. A new drawing or measurement names its equipment/configuration, date, method, result and uncertainty.

Rebuild and check the reading pages:

```text
python scripts/wiki.py
python scripts/wiki.py --check
python -m unittest discover -s tests -v
```

Propose the source change through a pull request so people can inspect the difference. Branch-review settings and named specialist reviewers are recorded as setup work until their actual configuration is checked. The review records below provide an additional, proposal-specific human decision trail.

## Record a person's decision

Each decision page shows its review scope and a content fingerprint: a SHA-256 identifier calculated from the exact proposal, supporting files, selected question evidence and source manifests. The named reviewer reads the package and posts the displayed `HITL APPROVE` line with `Conditions: none` in its linked GitHub issue. Put any conditions in that field; agreement then remains conditional until a fresh decision. An optional `Valid-until:` line records the date, time and timezone. Discuss reasons in a separate comment so the approval record stays unambiguous. `HITL CHANGE` and `HITL REJECT` record the other outcomes.

An authorised maintainer can then import the existing comment:

```text
python scripts/record_review.py --decision D-001 --role design_curator --comment-url COMMENT_URL
python scripts/wiki.py
```

The importer checks the actual comment, GitHub account, role, fingerprint and scope. Reviewer accounts for specialist/site/cultural/service roles are confirmed before those roles can approve. The published record makes the source comment visible. AI assistants prepare proposals and can import genuine decisions; the human approval comment is written by the person.

The checker re-reads recorded comments when rebuilding. Import any later change or withdrawal promptly and pause work affected by that change. This is a maintained decision record rather than a continuous monitor of every GitHub conversation. A changed proposal or supporting file receives a fresh fingerprint and returns to review; archive earlier records with `active: false` while retaining their history.

Private or formal approvals can use their own authorised process. Add a permitted public reference and confirm the verification method before using those records for an approval state. The first implementation checks public GitHub review comments.

## Publish the native GitHub Wiki

The `wiki/` pages are readable in the repository and are the source for the native Wiki. GitHub hosts a wiki in a separate Git repository. After its first page exists, clone it, export the checked pages into that checkout, inspect the changes and push the intended update:

```text
git clone https://github.com/auraofintelligence/aura-disaster-resilience.wiki.git
python scripts/wiki.py --export PATH_TO_WIKI_CHECKOUT
git -C PATH_TO_WIKI_CHECKOUT status
```

The export adapts links for native wiki navigation and preserves unrelated existing pages. Record the source commit and wiki publication commit in the publication notes. See [GitHub's wiki guide](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages).
