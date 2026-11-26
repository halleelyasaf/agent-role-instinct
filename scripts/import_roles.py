#!/usr/bin/env python3
"""Adapt every upstream Agency role for Instinct using only the standard library."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from validate_extensions import validate_extensions


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/msitarzewski/agency-agents"
ADAPTER = """## Using this role in Instinct

Apply this specialist's methods to the user's task while keeping Instinct's
identity, the user's preferences, and the chat's communication style. Give concise
updates; use an accessible file for a long deliverable when supported.

Use only the tools, connected apps, files, and account access actually available.
References below to other assistants, tool names, local paths, subagents, or
schedules are workflow examples to adapt to your environment. They do not grant
capabilities or permission. If separate agents are unavailable, apply the relevant
role perspectives yourself without claiming independent review.

Memory means information actually in the conversation or supported storage.
Treat the source persona's biography as a perspective, not your real history or
credentials. Adapt example dates, targets, and templates to the task.

Before applying the role, check the task, audience, required inputs, and any
relevant jurisdiction or time period against the full role's scope and limits.
Use facts already supplied; ask only for missing inputs that affect the result.
State unsupported scope and any better-matched role whose scope you have checked.
If none fits, say so and explain what useful work remains possible. An explicit
role request does not expand the role's supported scope. For specific tax
recommendations, establish the applicable jurisdictions and tax year first;
never assume US forms, entities, rates, or deadlines apply elsewhere.

At completion of work using this role, include a compact summary:

- Roles: each exact role name and catalog ID from the frontmatter, and what its
  methods contributed. A role perspective is not an independent reviewer.
- Checked: checks actually completed, their results, and evidence such as file
  locations, sources, or command output. Label static review versus execution.
- Not checked: checks not run, missing evidence or access, and remaining limits.

Keep this to a few lines when possible; do not imply unperformed verification.

This Instinct guidance, including any role-specific scope and application notes,
takes precedence over conflicting source instructions or metadata.
Follow existing platform instructions, the user's request, and current permissions.
"""


ROLE_ADAPTATIONS = {
    "finance/finance-tax-strategist": {
        "scope": (
            "Tax planning and compliance with substantial US-specific examples. "
            "Establish applicable jurisdictions and tax year before specific recommendations."
        ),
        "guidance": """### Tax scope and application

Confirm the applicable jurisdictions and tax year, using relevant residency,
entity, and cross-border facts already available. Ask for material missing facts
before recommending a form, entity structure, rate, deadline, or tax strategy.
US examples below (including IRS forms, S-Corps, and federal tax provisions) are
jurisdiction-specific references, not defaults for a non-US task. Verify rules
and applicability for the established jurisdictions and period. If the needed
facts or authoritative sources are unavailable, state the gap and limit the
output to general planning methods or questions rather than specific tax advice.
""",
    },
    "healthcare/healthcare-clinical-evidence-agent": {
        "scope": (
            "Clinical claim evidence and communication for healthcare startups and products; "
            "not personal medical advice, diagnosis, treatment, or prescribing."
        ),
        "guidance": """### Clinical evidence scope and application

Use this role for healthcare startup or product claims, evidence reviews, and
communications for the intended audience. Identify the claim or document,
audience, and available supporting evidence; state any material missing input.
Do not route a personal health question here as a diagnostic task. Explain the
scope mismatch and use the assistant's appropriate personal-health response
instead. Suggest another catalog role only after checking its actual scope; if
none supports the task, say so. The source's exclusions on medical advice,
diagnosis, treatment, and prescribing remain in force.
""",
    },
    "testing/testing-reality-checker": {
        "scope": (
            "Evidence-based review of implementations or non-code deliverables, including "
            "launch plans. Judge readiness from task-appropriate evidence, including on a first pass."
        ),
        "guidance": """### Reality Checker scope and application

The required outcome is an evidence-based comparison of claims and deliverables
with the task's acceptance criteria. Choose relevant checks from the actual
task, stack, artifacts, and available access. For a web project, use its own
tests and suitable browser or visual checks. The source's Laravel/HTML paths,
qa-playwright-capture.sh, localhost address, public/qa-screenshots directory,
test-results.json, and screenshot names are optional examples, even where the
source calls them mandatory. Equivalent project-specific checks are valid.

For a non-web deliverable such as a launch plan, review claims, assumptions,
sources, dependencies, and feasibility against the requested criteria. Do not
request irrelevant screenshots, web tooling, or local commands.

Separate observed defects (with evidence), missing evidence (claims remain
unverified), and checks not run (with reasons). Missing evidence is not proof of
a defect. Assess readiness within the reviewed scope from the results: report
observed defects as needing work and unsupported readiness claims as unverified.
A first-pass result may be ready when the relevant criteria are supported.
Do not require revision cycles, fixed grades, or automatic rejection of a first
implementation or a zero-defect report. Example performance thresholds apply
only when appropriate to the task's acceptance criteria. These notes override
the source's mandatory commands, automatic-fail rules, and default verdicts.
""",
    },
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def scalar(header, key, required=True):
    """Read the single-line string subset used by upstream's role metadata.

    Reject unsupported forms instead of silently losing descriptions. This is
    deliberately not a YAML loader and never constructs objects from source data.
    """
    matches = re.findall(rf"^{re.escape(key)}:[ \t]*(.*)$", header, re.MULTILINE)
    if not matches and not required:
        return ""
    if len(matches) != 1 or not matches[0].strip():
        raise ValueError(f"Expected one nonempty {key!r} field")
    value = matches[0].strip()
    if value.startswith('"'):
        value = json.loads(value)
    elif value.startswith("'"):
        if not value.endswith("'") or len(value) < 2:
            raise ValueError(f"Unterminated quoted {key!r}")
        value = value[1:-1].replace("''", "'")
    elif value.startswith(("|", ">", "[", "{", "&", "*", "!")):
        raise ValueError(f"Unsupported {key!r} syntax; extend the metadata reader")
    if not isinstance(value, str) or not value:
        raise ValueError(f"Expected a string for {key!r}")
    return value


def parse_role(data):
    text = data.decode("utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if not match:
        raise ValueError("Missing role frontmatter")
    header = match.group(1)
    metadata = {key: scalar(header, key) for key in ("name", "description")}
    for key in ("emoji", "color", "vibe"):
        value = scalar(header, key, required=False)
        if value:
            metadata[key] = value
    return metadata, text[match.end():]


def source_revision(source):
    revision = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("Expected a full Git commit hash")
    return revision


def build(source):
    revision = source_revision(source)
    divisions = json.loads((source / "divisions.json").read_text())["divisions"]
    for division in divisions:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", division):
            raise ValueError(f"Invalid division name: {division!r}")
    dirty = subprocess.check_output(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=normal",
         "--", "divisions.json", "LICENSE", *divisions], text=True
    )
    if dirty:
        raise ValueError("Source role files must match the recorded Git revision")

    files = {}
    roles = []
    counts = {}
    for division, details in divisions.items():
        paths = sorted((source / division).rglob("*.md"))
        if not paths:
            raise ValueError(f"Division has no roles: {division}")
        counts[division] = len(paths)
        for path in paths:
            if path.is_symlink() or source not in path.resolve().parents:
                raise ValueError(f"Role must be a regular file inside source: {path}")
            data = path.read_bytes()
            try:
                metadata, body = parse_role(data)
            except (ValueError, UnicodeError) as exc:
                raise ValueError(f"{path.relative_to(source)}: {exc}") from exc
            relative = path.relative_to(source).as_posix()
            output = f"roles/{relative}"
            url = f"{UPSTREAM}/blob/{revision}/{relative}"
            adaptation = ROLE_ADAPTATIONS.get(relative[:-3], {})
            scope = {"scope": adaptation["scope"]} if adaptation else {}
            portable = {
                "id": relative[:-3],
                **metadata,
                **scope,
                "division": division,
                "source": url,
            }
            header = "---\n" + "".join(
                f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
                for key, value in portable.items()
            ) + "---\n\n"
            attribution = (
                f"> Adapted from [Agency Agents: {metadata['name']}]({url}) "
                "under the [MIT license](" + "../" * len(PurePosixPath(output).parent.parts)
                + "LICENSE). The original specialist instructions are preserved below.\n\n"
            )
            # Keep every character after the upstream frontmatter intact.
            guidance = adaptation.get("guidance", "")
            if guidance:
                guidance = "\n" + guidance
            adapted = (header + attribution + ADAPTER + guidance
                       + "\n## Specialist instructions\n" + body).encode("utf-8")
            files[output] = adapted
            roles.append({
                "id": portable["id"],
                **metadata,
                **scope,
                "division": division,
                "division_label": details["label"],
                "path": output,
                "source": {"path": relative, "url": url, "sha256": digest(data)},
                "body_sha256": digest(body.encode("utf-8")),
                "sha256": digest(adapted),
            })

    index = ["# Role divisions", "", f"{len(roles)} roles across {len(divisions)} divisions.", "",
             "Read the relevant division index, then open the full role that matches the task.",
             "Check its scope, audience, required inputs, and applicable jurisdiction or period before using it.", ""]
    for division, details in divisions.items():
        index.append(f"- [{details['label']}]({division}/INDEX.md) — {counts[division]} roles")
        lines = [f"# {details['label']} roles", "", "[All divisions](../INDEX.md)", ""]
        for role in (r for r in roles if r["division"] == division):
            target = PurePosixPath(role["path"]).relative_to(PurePosixPath("roles") / division)
            description = " ".join(role["description"].split())
            scope_note = f" **Scope:** {role['scope']}" if "scope" in role else ""
            lines.append(f"- [{role['name']}]({target.as_posix()}) — {description}{scope_note}")
        files[f"roles/{division}/INDEX.md"] = ("\n".join(lines) + "\n").encode("utf-8")
    files["roles/INDEX.md"] = ("\n".join(index) + "\n").encode("utf-8")
    files["LICENSE"] = (source / "LICENSE").read_bytes()
    catalog = {
        "schema_version": 1,
        "upstream": {"repository": UPSTREAM, "commit": revision, "license": "MIT"},
        "role_count": len(roles),
        "divisions": {key: {**value, "role_count": counts[key]} for key, value in divisions.items()},
        "roles": roles,
        "generated_files": {name: digest(data) for name, data in sorted(files.items())},
    }
    files["catalog.json"] = (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return files, catalog


def reconcile(output, files, check=False):
    output = output.resolve()
    previous_path = output / "catalog.json"
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    managed = previous.get("generated_files", {})
    stale = set(managed) - files.keys()
    differences = [name for name, data in files.items()
                   if not (output / name).is_file() or (output / name).read_bytes() != data]
    extras = {p.relative_to(output).as_posix() for p in (output / "roles").rglob("*.md")} - files.keys()
    if check:
        problems = sorted(set(differences) | stale | extras)
        if problems:
            raise ValueError("Generated files differ: " + ", ".join(problems[:15]))
        return

    # Validate all destinations before writing anything. Do not clobber local edits.
    for name in set(differences) | stale:
        path = output / name
        if path.is_symlink() or output not in path.resolve().parents:
            raise ValueError(f"Unsafe generated destination: {name}")
        if path.exists() and name != "catalog.json":
            existing_hash = digest(path.read_bytes())
            if existing_hash != managed.get(name):
                raise ValueError(f"Local changes in {name}; preserve them before regenerating")
    for name in stale:
        (output / name).unlink(missing_ok=True)
    for name in differences:
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(files[name])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Clean local agency-agents Git checkout")
    parser.add_argument("--check", action="store_true", help="Verify generated files without writing")
    args = parser.parse_args()
    try:
        files, catalog = build(args.source.resolve())
        extensions = validate_extensions(ROOT, catalog)
        reconcile(ROOT, files, check=args.check)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"error: {exc}\n")
    verb = "Verified" if args.check else "Imported"
    print(f"{verb} {catalog['role_count']} roles across {len(catalog['divisions'])} divisions "
          f"from {catalog['upstream']['commit']}; {len(extensions['extensions'])} original extension(s) validated")


if __name__ == "__main__":
    main()
