# Continue the Aura Disaster Resilience workshop

**Checkpoint: 20 October 2026, Australia/Brisbane. Read this file first after a context or chat change.**

The user's requested home is https://github.com/auraofintelligence/aura-disaster-resilience. The local checkout is this repository. The work is an optimistic, practical GitHub wiki for a complete disaster kiosk and resilience network, connected to the wider ecosystem through clearly defined interfaces.

## The people this is for

Assume an average Australian with no prior knowledge or formal degree who learns quickly by doing: tradespeople, trade assistants, drivers, artists, nurses, carers, retirees, students and technical/policy readers alike. Explain what each part helps someone do and how to work on it. Explain unfamiliar terms, welcome practical knowledge and show useful next steps. Keep ambition and accurate stage/evidence together.

## Directions to carry forward

- The immediate delivery focus is the kiosk and network, everyday usefulness plus demanding disaster operation. Wider projects provide interfaces and growth paths.
- Ready S.E.T. Co-op, fully Ready Sustainable Employment and Training Cooperative, is the proposed intermediary. Use that exact naming. Planning/design are underway; community discussion, construction, operating services and field validation remain future milestones.
- Aura of Intelligence is the personal AI operating system Luke is designing from light to ultra high definition, navigating the network and supporting just-in-time learning. Personal-model depth, presentation, compute location and emergency power mode are separate choices/states. Public assistance is available without a personal profile.
- GAJRA Earth, Global Association for Joyful Responsible Abundance on Earth, is the values starting point. Preserve personal agency, local/cultural authority, meaningful choice, consequences and wider useful capability.
- A C-Hour recognises one verified voluntary human hour. Communities choose reciprocal rewards. There is no monetary equivalent, sale or transfer. Paid work, money, machine time and outcomes have separate records; count each person's elapsed contribution once across linked projects.
- Use Purple Party for Australia or P4A. Preserve the older repository slug in source links. The intended referendum horizon is during or before 2031 with a hoped-for Brisbane 2032 showcase.
- The original Dig for Australia chat is unlocated; supplied food and place documents are the closest sources. Continue from them without asking again for that chat.
- The visual artwork is inspiration. The all-weather design needs its own exposure requirements, drawings, energy and thermal measurements, access, maintenance and appropriate reviews.
- The user explicitly requests all supplied documents and referenced sites uploaded here, rights preserved using their established Strange But True licence and usual robots pattern, and a durable agent/swarm handover.

## Working records and architecture

The source of truth will be readable JSON records in data/ plus longer pages in content/. scripts/wiki.py produces linked Markdown in wiki/ for repository browsing and native GitHub Wiki export. The native wiki uses a separate Git repository. The new repository began empty and was initialised locally on main with the intended origin. Publishing status must be checked before claiming completion.

Three seed sets provide 90 questions across OPS, DAT, GOV, FIN, TEST, PHY, ENE, COM, SW, AUR, TWIN and ECO. The integrator adds six WRK questions, giving 96 questions in 13 work areas. IDs and connected questions are stable. Source seed files are in the predecessor task workspace; data/questions.json will become the maintained record after assembly.

Three initial review packages are prepared: D-001 working method, D-002 weather-ready kiosk design brief, D-003 connected service demonstration. They are proposals awaiting human decisions. No human approval has been inferred or created. D-002 covers design work; later engineering, sites and operation have their own people and evidence.

The review helper imports an existing named person's GitHub issue comment, checking its exact proposal fingerprint, scope and configured role. Agents never write source approval comments in a person's name. data/roles.json names the project owner's account for project-design reviews; specialist/site/cultural/service/public-authority accounts await confirmation. Branch protection and a continuous review monitor are separate setup items; do not claim them configured without checking.

## Checkpoint work still to finish

1. Assemble data from the final plain-language seed files, finish source register and workflow files, build the wiki and run meaningful tests. Resolve dependency cycles or missing links with explicit design reasoning.
2. Integrate the document and site packages with manifests, full checksums, deduplication aliases and restore/verification helpers. Keep actual source bytes, original filenames/rights and source snapshots. Exclude private credentials, caches and the temporary UI screenshot. Check large-file and push sizes.
3. Integrate the established licence and crawler-discovery files. A project robots.txt records preferences; effective crawler rules belong at the website origin root. Native GitHub Wiki uses GitHub's own origin rules.
4. Publish the checked source repository, create the three human-review issue conversations, write their links into data/decisions.json and rebuild without changing the proposal scope.
5. Initialise the native GitHub Wiki if needed, export the checked pages, publish and verify reading/navigation. If browser sign-in or first-page creation is the remaining obstacle, finish the fully usable repository wiki and clearly report the precise remaining native-tab step.
6. Check GitHub automated runs, source availability, public document/site download links, user-facing language and human-review records. Update this handover with exact commits and outcomes.

## Files and jobs in progress at this checkpoint

- Root integrator: scripts/wiki.py, scripts/record_review.py, tests/test_wiki.py, README, AGENTS, CONTRIBUTING, initial records, GitHub publication and this handover.
- audit_existing_repo: sources for 30 hardware questions and content/All-weather-design.md complete; now owns LICENCE.md, robots.txt, .github/robots-root-snippet.txt and content/Rights-and-discovery.md.
- review_source_pdfs: 30 software/Aura/twin/interface questions and workflow templates complete; now owns sources/documents/, data/document-manifest.json and scripts/verify_documents.py.
- verify_planning_sources: 30 service/governance/funding/test questions, 31 ecosystem groups/43 repository destinations and content/Stack-map.md complete; now owns sources/sites/, data/site-manifest.json, scripts/verify_sites.py and scripts/restore_site.py.

Shared files must have one editor at a time. Check agent status or the filesystem before redoing work. Preserve earlier source repositories and their unrelated changes.

## Commands and runtime

Use Python 3.12 or newer and Git. The bundled Windows runtime paths were discovered in this chat; a new chat can call load_workspace_dependencies to locate them. The build uses Python's standard library.

```text
python scripts/wiki.py
python scripts/wiki.py --check
python -m unittest discover -s tests -v
python scripts/verify_documents.py
python scripts/verify_sites.py
```

The earlier local planning and source register remain in the predecessor straddie-disaster-kiosks/docs directory. The user supplied that as lineage, then selected aura-disaster-resilience as the destination. The new question-driven wiki supersedes the predecessor's flat implementation-decision list.
