#!/usr/bin/env python3
"""Package the complete portable role library; omit Git state and build tools."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def package(destination):
    catalog = json.loads((ROOT / "catalog.json").read_text())
    # Reject incomplete or edited imports before producing a transferable artifact.
    for name, expected in catalog["generated_files"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Generated file differs from catalog: {name}")
    names = {"README.md", "INSTINCT.md", "SKILL.md", "LICENSE", "NOTICE", "catalog.json"}
    names.update(role["path"] for role in catalog["roles"])
    names.update(name for name in catalog["generated_files"] if name.endswith("/INDEX.md"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(names):
            info = zipfile.ZipInfo(f"agent-role-instinct/{name}", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / name).read_bytes())
    print(f"Packaged {catalog['role_count']} roles in {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/agent-role-instinct.zip")
    args = parser.parse_args()
    try:
        package(args.output.resolve())
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    main()
