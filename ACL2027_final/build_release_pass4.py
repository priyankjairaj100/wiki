#!/usr/bin/env python3
"""Package verified pass-4 sources, a compiled paper, and an Overleaf project.

Run --refresh-manifest after the final edits, then python reproduce.py.
Run --package after that verification succeeds. No inference is started.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
RELEASE = 'ACL2027_pass4'
SKIP_DIRS = {'__pycache__', 'cache', '.git', '.venv', 'node_modules',
             'reproduced', 'reproduced_pass3', 'reproduced_pass4', 'access_probes'}
AUX_SUFFIXES = {'.aux', '.bbl', '.blg', '.out', '.toc', '.fls', '.fdb_latexmk', '.synctex.gz', '.pyc'}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def release_files():
    for path in sorted(ROOT.rglob('*')):
        rel = path.relative_to(ROOT)
        if any(p in SKIP_DIRS or p.startswith('.') for p in rel.parts):
            continue
        if not path.is_file() or path.is_symlink() or path.suffix in AUX_SUFFIXES:
            continue
        if path.name == 'MANIFEST.json' and len(rel.parts) == 1:
            continue
        if path.suffix in {'.gguf', '.so'} or '.so.' in path.name:
            raise RuntimeError('Unexpected model/runtime asset in source tree: ' + str(rel))
        yield path


def write_atomic(destination, writer):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.writing')
    try:
        with temporary.open('wb') as stream:
            writer(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def refresh_manifest():
    files = {str(path.relative_to(ROOT)): digest(path) for path in release_files()}
    value = {'release': RELEASE, 'files': files}
    payload = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()
    write_atomic(ROOT / 'MANIFEST.json', lambda stream: stream.write(payload))
    print(json.dumps({'manifest_files': len(files), 'sha256': digest(ROOT / 'MANIFEST.json')}), flush=True)


def verify_manifest():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    if manifest.get('release') != RELEASE:
        raise RuntimeError('Refresh the pass-4 manifest first.')
    files = manifest['files']
    current = {str(path.relative_to(ROOT)) for path in release_files()}
    if current != set(files):
        raise RuntimeError('Manifest membership changed. Refresh and verify before packaging.')
    for name, expected in files.items():
        if digest(ROOT / name) != expected:
            raise RuntimeError('Release hash mismatch: ' + name)
    return manifest


def require_complete_reader():
    for track, count in [('human', 193), ('human_diagnostic', 45)]:
        path = ROOT / 'pass4/inference' / track / 'reader_output.manifest.json'
        manifest = json.loads(path.read_text())
        if manifest.get('rows') != count or manifest.get('output_rows') != count:
            raise RuntimeError('Incomplete reader batch: ' + track)
    text = (ROOT / 'pass4/paper/sections/reader_results.tex').read_text()
    if len(text.split()) < 70 or any(word in text.lower() for word in ['todo', 'pending', 'placeholder']):
        raise RuntimeError('Reader results must be finalized before packaging.')


def make_zip(path, members):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for source, name in members:
            archive.write(source, name)
    with path.open('rb') as stream:
        os.fsync(stream.fileno())
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError('Archive CRC failure: ' + bad)
        return len(archive.namelist())


def copy_atomic(source, destination):
    with Path(source).open('rb') as original:
        write_atomic(destination, lambda stream: shutil.copyfileobj(original, stream, 4 * 1024 * 1024))
    if digest(source) != digest(destination):
        raise RuntimeError('Final copy checksum mismatch: ' + str(destination))


def package(destination):
    manifest = verify_manifest()
    require_complete_reader()
    destination = Path(destination).resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise RuntimeError('Choose a deliverable directory outside the source tree.')
    checks = json.loads((ROOT / 'pass4/audit/release/PAPER_CHECKS.json').read_text())
    if checks.get('main_pages') != 8 or checks.get('limitations_start_page') != 9:
        raise RuntimeError('The accepted paper must have eight main pages.')
    if checks.get('pdf_sha256') != digest(ROOT / 'pass4/paper/main.pdf'):
        raise RuntimeError('PDF differs from the accepted layout audit.')
    reports = list((ROOT / 'reproduced_pass4').glob('verification_*/verification.json'))
    matching = []
    manifest_sha = digest(ROOT / 'MANIFEST.json')
    for report in reports:
        value = json.loads(report.read_text())
        saved = value.get('checks', {}).get('release_manifest', {})
        if value.get('status') == 'passed' and saved.get('sha256') == manifest_sha:
            matching.append(report)
    if not matching:
        raise RuntimeError('Run python reproduce.py successfully against this exact manifest before packaging.')
    destination.mkdir(parents=True, exist_ok=True)
    outputs = []
    with tempfile.TemporaryDirectory(prefix='acl2027-pass4-package-') as temporary:
        stage = Path(temporary)
        source_name = RELEASE + '_source_and_runs.zip'
        overleaf_name = RELEASE + '_overleaf.zip'
        pdf_name = RELEASE + '_paper.pdf'
        source_members = [(ROOT / name, RELEASE + '/' + name) for name in sorted(manifest['files'])]
        source_members.append((ROOT / 'MANIFEST.json', RELEASE + '/MANIFEST.json'))
        make_zip(stage / source_name, source_members)
        paper = ROOT / 'pass4/paper'
        overleaf_members = []
        for path in sorted(paper.rglob('*')):
            if path.is_file() and path.suffix in {'.tex', '.bib', '.bst', '.sty', '.pdf', '.svg', '.png', '.txt'}:
                overleaf_members.append((path, str(path.relative_to(paper))))
        make_zip(stage / overleaf_name, overleaf_members)
        shutil.copyfile(paper / 'main.pdf', stage / pdf_name)
        for name in [pdf_name, overleaf_name, source_name]:
            final = destination / name
            copy_atomic(stage / name, final)
            outputs.append({'path': str(final), 'bytes': final.stat().st_size, 'sha256': digest(final)})
    receipt = {'release': RELEASE, 'verified_manifest_sha256': manifest_sha,
               'verification_report': str(sorted(matching)[-1].relative_to(ROOT)), 'outputs': outputs}
    write_atomic(destination / (RELEASE + '_deliverables.json'),
                 lambda stream: stream.write((json.dumps(receipt, indent=2) + '\n').encode()))
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-manifest', action='store_true')
    parser.add_argument('--package', action='store_true')
    parser.add_argument('--destination', type=Path, default=ROOT.parent / 'deliverables_pass4')
    args = parser.parse_args()
    if not args.refresh_manifest and not args.package:
        parser.error('Choose --refresh-manifest or --package.')
    if args.refresh_manifest:
        refresh_manifest()
    if args.package:
        package(args.destination)
