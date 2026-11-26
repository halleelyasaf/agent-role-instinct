# Agency roles for Instinct

All **283 roles across 18 divisions** from [agency-agents](https://github.com/msitarzewski/agency-agents), adapted into Markdown that the **Instinct AI personal assistant** can read and use.

Start with [INSTINCT.md](INSTINCT.md): it contains a message to paste into Instinct. Give it this folder or the ZIP created below. If you publish this repository, you can give Instinct its GitHub URL instead.

Example requests after loading the library:

- “Use the Frontend Developer role to improve my website.”
- “Use the Personal Growth Mentor role to build a weekly plan for my goals.”
- “Use the Reality Checker role to review this launch plan.”
- “Choose the best role for this task: help me prepare for a sales discovery call.”

## What's included

- [SKILL.md](SKILL.md): a small entry point for assistants that support Markdown skills.
- [Role index](roles/INDEX.md): divisions, role descriptions, and links to every role.
- [catalog.json](catalog.json): the full machine-readable catalog, pinned upstream revision, source links, integrity hashes, and role-specific scope notes where present.
- `roles/`: every original role's full instructions, examples, and workflows, with an Instinct adaptation at the top.

Instinct chooses the relevant role rather than loading the whole library into every conversation. Each role keeps its specialist knowledge while using Instinct's chat style and the apps, browser, files, or other tools actually available to it. Role-specific tool lists do not grant tools or account access. Memory and completed actions must reflect what Instinct has actually stored or done.

Selection includes a scope check against the task, audience, required inputs, and relevant jurisdiction or time period. Tax Strategist requires applicable jurisdictions and a tax year before specific recommendations; US examples are not defaults for other countries. Clinical Evidence Agent supports healthcare startup and product claims rather than personal medical advice or diagnosis. Reality Checker can review code or a launch plan using task-appropriate evidence; its preserved web commands are examples, and first-pass work is judged on results.

These are portable Markdown instructions. There is no claim of a verified native importer or installation path for the hosted Instinct product. A role can also be used by giving Instinct the individual Markdown file. This project is independent of Instinct and the upstream Agency Agents project.

## Original extensions

In addition to the 283 upstream-adapted roles, this library includes **1 original extension**: [Task Role Coordinator](extensions/task-role-coordinator.md). It selects roles afresh per task and tracks focused recommendations and responses. See the [separate extension index](extensions/INDEX.md) and [manifest](extensions/manifest.json). It is standalone guidance, not tested on a real task or enforced by a website. It is not part of catalog.json; website integration is a separate change. Original extensions are preserved during upstream regeneration and included separately in the ZIP.

## Completion examples

Every task using the library ends with a short summary of the exact roles and their contributions, checks completed with evidence, and checks not completed or remaining limits. These hypothetical examples illustrate the format; they do not report tests run on this library. Applying two role perspectives does not constitute independent review.

Single-role launch-plan review using supplied documents:

> **Roles:** Reality Checker (`testing/testing-reality-checker`) — compared launch claims, owners, and dependencies with the plan's acceptance criteria.
>
> **Checked (static review):** Compared the milestone and owner lists in the supplied `launch-plan.md`; the launch milestone has no assigned owner (Milestones, item 4).
>
> **Not checked:** Customer demand and budget claims remain unverified because supporting evidence was not supplied. No commands, browser checks, or live launch-system tests were run.

Multi-role web change in a project with executable tests:

> **Roles:** Frontend Developer (`engineering/engineering-frontend-developer`) — implemented form validation; Reality Checker (`testing/testing-reality-checker`) — compared form behavior with the project's acceptance criteria.
>
> **Checked (execution):** The project's `npm test` passed (`test-output.txt`); a browser check confirmed empty submissions show the required-field message (`form-check.webm`).
>
> **Not checked:** Cross-browser compatibility and production deployment were not tested; readiness is limited to the tested environment and behaviors.

## Create a transferable ZIP

Requires Python 3.9 or later; no additional packages.

```sh
python3 scripts/package_roles.py
```

This creates `dist/agent-role-instinct.zip`, containing the entry point, installation message, catalog, all role files, and license. Give the ZIP to Instinct if your chat supports attachments; otherwise share a reachable repository URL or an individual role's text.

## Refresh from upstream

```sh
git clone https://github.com/msitarzewski/agency-agents.git /tmp/agency-agents
python3 scripts/import_roles.py /tmp/agency-agents
python3 scripts/import_roles.py /tmp/agency-agents --check
```

The importer recursively reads every division in upstream `divisions.json`, including nested game-development roles. It preserves the source bodies, converts role metadata, adds Instinct guidance, and regenerates the indexes and catalog. It records the exact commit and hashes. It refuses to overwrite local changes to previously generated files; edit `ADAPTER` or `ROLE_ADAPTATIONS` in the importer to make lasting changes to the shared guidance or role-specific scope and application notes. Those notes control interpretation of conflicting preserved instructions. Review upstream changes before using the refreshed library.

`--check` verifies completeness and exact generated content without changing files. The importer reads a local checkout and does not execute upstream scripts. Upstream role bodies and code examples are preserved as reference material; they have not all been executed or independently validated.

## Attribution

Adapted from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents). Original role content is distributed under the [MIT license](LICENSE), including its original copyright notice. See [NOTICE](NOTICE) for the adaptation details and `catalog.json` for the pinned source revision.

## Testing original extensions

Run `python -m unittest discover -s tests -v`. For regeneration and package tests, set `AGENCY_SOURCE` to a clean checkout at the commit recorded in catalog.json. The test fixture normalizes a pre-existing upstream-role hash mismatch only inside a disposable copy. In the repository baseline, `roles/security/security-secrets-credential-engineer.md` has an extra `notsecret` annotation that does not match its catalog hash. Consequently full-repository import checking and packaging currently fail on that file. This extension change preserves that file and catalog.json unchanged; it does not bypass the check or silently repair the mismatch.
