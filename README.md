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
- [catalog.json](catalog.json): the full machine-readable catalog, pinned upstream revision, source links, and integrity hashes.
- `roles/`: every original role's full instructions, examples, and workflows, with an Instinct adaptation at the top.

Instinct chooses the relevant role rather than loading the whole library into every conversation. Each role keeps its specialist knowledge while using Instinct's chat style and the apps, browser, files, or other tools actually available to it. Role-specific tool lists do not grant tools or account access. Memory and completed actions must reflect what Instinct has actually stored or done.

These are portable Markdown instructions. There is no claim of a verified native importer or installation path for the hosted Instinct product. A role can also be used by giving Instinct the individual Markdown file. This project is independent of Instinct and the upstream Agency Agents project.

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

The importer recursively reads every division in upstream `divisions.json`, including nested game-development roles. It preserves the source bodies, converts role metadata, adds Instinct guidance, and regenerates the indexes and catalog. It records the exact commit and hashes. It refuses to overwrite local changes to previously generated files; edit the importer to make lasting changes to the adapter. Review upstream changes before using the refreshed library.

`--check` verifies completeness and exact generated content without changing files. The importer reads a local checkout and does not execute upstream scripts. Upstream role bodies and code examples are preserved as reference material; they have not all been executed or independently validated.

## Attribution

Adapted from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents). Original role content is distributed under the [MIT license](LICENSE), including its original copyright notice. See [NOTICE](NOTICE) for the adaptation details and `catalog.json` for the pinned source revision.
