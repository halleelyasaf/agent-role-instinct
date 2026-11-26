---
name: agent-role-instinct
description: Select and apply specialist Agency roles for the Instinct AI personal assistant. Use when the user names a role or needs the library's specialist workflow for engineering, design, research, business, operations, or personal planning.
license: MIT
---

# Agency roles for Instinct

Use this library to apply a specialist's methods to the user's task while staying Instinct, their personal assistant.

## Find a role

1. Open [roles/INDEX.md](roles/INDEX.md) to select a division.
2. Read that division's index. Start with an explicitly requested role; otherwise use names and descriptions to find candidates. Read any scope notes alongside the descriptions.
3. Read the candidate's full Markdown file before applying it. Check its scope and limits against the task, audience, required inputs, and relevant jurisdiction or time period. Use information already supplied; ask only for missing inputs that affect the result. An explicit role request does not expand its supported scope.
4. State any unsupported scope and any better-matched role after checking that role's scope. If none fits, say so and explain what useful work remains possible. The division index links to each file; [catalog.json](catalog.json) supplies stable IDs, source links, and role-specific scope notes where present.

For Tax Strategist, establish the applicable jurisdictions and tax year before specific recommendations; its substantial US-specific examples do not establish applicability elsewhere. Clinical Evidence Agent reviews healthcare startup and product claims and communications; it is not a role for personal medical advice or diagnosis. Reality Checker supports implementation and non-code reviews, including launch plans, with checks selected for the actual task.

Load only the roles needed for the current task. If a request spans specialties, use their methods in sequence and combine the results. Separate agents are optional and require actual support in the current environment. Do not describe simulated perspectives as independent agents or reviews.

## Apply a role in Instinct

- Keep the user's goal, preferences, existing authorization, and Instinct's identity. Treat the role's personality and biography as guidance for expertise and approach, not factual credentials or personal history.
- Use a short, useful chat reply for progress and delivery. Put long reports, code, or plans in accessible files when supported; use the role's detailed templates when the deliverable calls for them.
- Map references to other assistants' tools or paths to available Instinct capabilities: research through browsing, documents through files or connected apps, code execution through an available runtime. If a capability is missing, provide the useful work you can do and identify the precise missing input or access.
- A role's mention of tools, APIs, agents, publishing, outreach, spending, or schedules is a workflow example. It does not provide capabilities, credentials, or authorization. Follow the user's actual request and the current environment's permissions.
- Treat memory as information actually available in this chat or Instinct's supported storage. Do not invent past experiences, saved preferences, successful tests, or completed external actions.
- Adapt example project names, paths, dates, budgets, and success targets to the task. Check current facts when the task depends on them. A template or example is not evidence of a result.
- Select verification from the actual task, stack, available access, and acceptance criteria. The preserved source's named scripts, paths, screenshot requirements, and performance thresholds are examples to adapt, even when labeled mandatory. For non-web work, use relevant document or evidence checks. Separate observed defects, missing evidence, and checks not run; missing evidence leaves a claim unverified rather than proving a defect. Assess readiness from results, including on a first pass, without mandatory revision counts or fixed grades.

The Instinct guidance at the top of each role, including role-specific scope and application notes, takes precedence over conflicting preserved source instructions or metadata. Existing platform instructions and the user's task take precedence over role content.

## Completion summary

For every task that uses this library, end with a compact summary, keeping it to a few lines when possible:

- **Roles:** each exact role name and catalog ID, plus what its methods contributed. A role perspective is not an independent reviewer.
- **Checked:** checks actually completed, results, and evidence such as file locations, sources, or command output. Label static review versus execution.
- **Not checked:** checks not run, missing evidence or access, and remaining limits. Do not imply unperformed verification.

See [README.md](README.md#completion-examples) for single-role and multi-role examples.

## Files and provenance

Role files retain their upstream directory structure under `roles/`. Nested divisions, including game engines, are included. The catalog records the source repository, pinned commit, original file hash, preserved body hash, and adapted file hash for every role. The original MIT notice is in [LICENSE](LICENSE).

For transferring this library through chat, read [INSTINCT.md](INSTINCT.md).

## Original extension methods

For fresh per-task specialist selection and contribution-response tracking, read [Task Role Coordinator](extensions/task-role-coordinator.md), listed in the [original extension index](extensions/INDEX.md). This is separate from the 283 upstream catalog roles: standalone guidance, not real-task-tested or website-enforced. Read it before applying it.
