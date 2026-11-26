"""Validate original extensions separately from the immutable upstream catalog."""
import hashlib
import json
from pathlib import Path
import re


def validate_extensions(root, catalog):
    root = Path(root).resolve()
    if (root / 'extensions').is_symlink():
        raise ValueError('Extension directory must not be a symlink')
    manifest_path = root / 'extensions/manifest.json'
    if manifest_path.is_symlink():
        raise ValueError('Extension manifest must be a regular file')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if set(manifest) != {'schema_version', 'kind', 'extensions'} or manifest['schema_version'] != 1 or manifest['kind'] != 'original-role-extensions':
        raise ValueError('Invalid extension manifest')
    entries = manifest['extensions']
    if not isinstance(entries, list) or not entries or len(entries) > 100:
        raise ValueError('Invalid extension count')
    ids = {r['id'] for r in catalog['roles']}
    paths = set()
    required = {'id', 'name', 'path', 'sha256', 'provenance', 'description', 'limits'}
    for e in entries:
        if not isinstance(e, dict) or set(e) != required or any(not isinstance(v, str) or not v.strip() for v in e.values()):
            raise ValueError('Invalid extension fields or false source metadata')
        if not re.fullmatch(r'[a-z0-9-]+/[a-z0-9-]+', e['id']) or e['id'] in ids:
            raise ValueError('Duplicate or invalid extension ID')
        ids.add(e['id'])
        if not re.fullmatch(r'extensions/[a-z0-9-]+\.md', e['path']) or e['path'] in paths:
            raise ValueError('Unsafe or duplicate extension path')
        paths.add(e['path'])
        p = root / e['path']
        if p.is_symlink() or not p.is_file() or root not in p.resolve().parents:
            raise ValueError('Missing or unsafe extension file')
        data = p.read_bytes()
        if len(data) > 100000 or hashlib.sha256(data).hexdigest() != e['sha256'] or e['provenance'] != 'original-authored-not-upstream':
            raise ValueError('Extension integrity or provenance mismatch')
        text = data.decode('utf-8')
        if not text.startswith('---\n') or '\n---\n' not in text[4:]:
            raise ValueError('Missing extension frontmatter')
        header = text.split('---', 2)[1]
        fields = {}
        for line in header.strip().splitlines():
            key, sep, value = line.partition(':')
            if not sep or key in fields:
                raise ValueError('Invalid extension frontmatter')
            fields[key] = json.loads(value.strip())
        if set(fields) != {'id', 'name', 'description', 'emoji', 'color', 'division', 'vibe', 'status'}:
            raise ValueError('Unexpected extension frontmatter fields')
        if fields.get('id') != e['id'] or fields.get('name') != e['name'] or fields.get('division') != e['id'].split('/')[0] or any(k.startswith('source') for k in fields) or fields.get('status') != 'Standalone proposed role, not catalog-integrated.':
            raise ValueError('Extension metadata mismatch')
        if 'original method' not in text or 'not yet a catalog entry' not in text:
            raise ValueError('Original standalone provenance must be explicit')
    actual = {p.relative_to(root).as_posix() for p in (root / 'extensions').rglob('*.md') if p.name != 'INDEX.md'}
    if actual != paths:
        raise ValueError('Unlisted extension file')
    index = root / 'extensions/INDEX.md'
    if index.is_symlink() or not index.is_file():
        raise ValueError('Missing extension index')
    for e in entries:
        if Path(e['path']).name not in index.read_text(encoding='utf-8'):
            raise ValueError('Extension missing from index')
    return manifest
