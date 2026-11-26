"""Original extension validation and packaging tests (standard library only).

Run python -m unittest discover -s tests -v.
Set AGENCY_SOURCE to a clean pinned upstream checkout for regeneration tests.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_extensions import validate_extensions
import import_roles
import package_roles


class Extensions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist'))
        self.catalog = json.loads((self.root / 'catalog.json').read_text())
        self.manifest = json.loads((self.root / 'extensions/manifest.json').read_text())

    def save(self):
        (self.root / 'extensions/manifest.json').write_text(json.dumps(self.manifest))

    def validate(self):
        return validate_extensions(self.root, self.catalog)

    def test_valid_exact_role(self):
        result = self.validate()
        self.assertEqual(len(result['extensions']), 1)
        self.assertEqual(result['extensions'][0]['sha256'], 'adfd9a2a512444539ff889a7e6bad98de6e2726ba53787df7038f8eacaa31562')

    def test_bad_manifest_shapes(self):
        for data in ({}, {'schema_version': 2}, {'schema_version': 1, 'kind': 'original-role-extensions', 'extensions': []}):
            with self.subTest(data=data):
                (self.root / 'extensions/manifest.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError): self.validate()
        (self.root / 'extensions/manifest.json').write_text('{')
        with self.assertRaises(ValueError): self.validate()

    def test_missing_directory(self):
        shutil.rmtree(self.root / 'extensions')
        with self.assertRaises(OSError): self.validate()

    def test_metadata_collisions_sources_paths(self):
        original = copy.deepcopy(self.manifest)
        variants = [dict(id=self.catalog['roles'][0]['id']), dict(provenance='upstream'), dict(source='invented'), dict(path='../README.md'), dict(path='/tmp/outside.md')]
        for change in variants:
            self.manifest = copy.deepcopy(original)
            self.manifest['extensions'][0].update(change); self.save()
            with self.subTest(change=change), self.assertRaises(ValueError): self.validate()
        self.manifest = copy.deepcopy(original)
        self.manifest['extensions'].append(copy.deepcopy(self.manifest['extensions'][0])); self.save()
        with self.assertRaises(ValueError): self.validate()

    def test_hash_tamper(self):
        p = self.root / self.manifest['extensions'][0]['path']
        p.write_bytes(p.read_bytes() + b'changed')
        with self.assertRaises(ValueError): self.validate()

    def test_frontmatter_source_and_identity(self):
        p = self.root / self.manifest['extensions'][0]['path']; original = p.read_text()
        for text in (original.replace('specialized/task-role-coordinator', 'specialized/wrong'), original.replace('status:', 'source: "invented"\nstatus:'), original.replace('---\n', '', 1)):
            p.write_text(text)
            self.manifest['extensions'][0]['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest(); self.save()
            with self.assertRaises(ValueError): self.validate()

    def test_missing_unlisted_symlink_index(self):
        p = self.root / 'extensions/unlisted.md'; p.write_text('extra')
        with self.assertRaises(ValueError): self.validate()
        p.unlink(); index = self.root / 'extensions/INDEX.md'; index.unlink()
        with self.assertRaises(ValueError): self.validate()
        index.write_text('no link')
        with self.assertRaises(ValueError): self.validate()

    def test_symlink_role(self):
        p = self.root / self.manifest['extensions'][0]['path']; data = p.read_bytes(); p.unlink()
        target = Path(self.tmp.name) / 'target.md'; target.write_bytes(data); p.symlink_to(target)
        with self.assertRaises(ValueError): self.validate()

    @unittest.skipUnless(os.environ.get('AGENCY_SOURCE'), 'Set AGENCY_SOURCE for full regeneration/package checks')
    def test_regenerate_twice_check_and_package(self):
        source = Path(os.environ['AGENCY_SOURCE'])
        files, generated_catalog = import_roles.build(source)
        # Normalize only this disposable fixture. A pre-existing repository file
        # has an extra notsecret annotation whose hash differs from catalog.json.
        for name, data in files.items(): (self.root / name).write_bytes(data)
        for name in ('README.md', 'SKILL.md'):
            self.assertNotIn(name, files)
            self.assertIn('Task Role Coordinator', (self.root / name).read_text())
        entrypoint_before = {name: (self.root / name).read_bytes() for name in ('README.md', 'SKILL.md')}
        expected = {p: (self.root / p).read_bytes() for p in files}
        extension_before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in (self.root / 'extensions').rglob('*') if p.is_file()}
        for _ in range(2):
            self.assertEqual(subprocess.run([sys.executable, str(self.root / 'scripts/import_roles.py'), str(source)], capture_output=True).returncode, 0)
        self.assertEqual(subprocess.run([sys.executable, str(self.root / 'scripts/import_roles.py'), str(source), '--check'], capture_output=True).returncode, 0)
        for name, data in entrypoint_before.items():
            self.assertEqual((self.root / name).read_bytes(), data)
            self.assertIn('extensions/task-role-coordinator.md', (self.root / name).read_text())
        self.assertEqual(expected, {p: (self.root / p).read_bytes() for p in files})
        self.assertEqual(extension_before, {p: (self.root / p).read_bytes() for p in extension_before})
        old = package_roles.ROOT; package_roles.ROOT = self.root
        try:
            a = Path(self.tmp.name) / 'a.zip'; b = Path(self.tmp.name) / 'b.zip'
            package_roles.package(a); package_roles.package(b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with zipfile.ZipFile(a) as z:
                prefix = 'agent-role-instinct/'
                self.assertEqual(z.read(prefix + 'catalog.json'), expected['catalog.json'])
                for p, data in extension_before.items(): self.assertEqual(z.read(prefix + p), data)
                self.assertEqual(sum(n.startswith(prefix+'roles/') and not n.endswith('/INDEX.md') for n in z.namelist()), 283)
            extension = self.root / self.manifest['extensions'][0]['path']
            original_extension = extension.read_bytes()
            extension.write_bytes(original_extension + b'changed')
            with self.assertRaises(ValueError): package_roles.package(b)
            self.assertNotEqual(subprocess.run([sys.executable, str(self.root / 'scripts/import_roles.py'), str(source), '--check'], capture_output=True).returncode, 0)
            extension.write_bytes(original_extension)
            target = self.root / self.catalog['roles'][0]['path']; target.write_bytes(target.read_bytes() + b'changed')
            self.assertNotEqual(subprocess.run([sys.executable, str(self.root / 'scripts/import_roles.py'), str(source), '--check'], capture_output=True).returncode, 0)
            with self.assertRaises(ValueError): package_roles.package(b)
        finally: package_roles.ROOT = old


if __name__ == '__main__': unittest.main()
