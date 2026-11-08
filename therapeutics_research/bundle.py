"""Exact, exclusive offline bundles. Replay is consistency, not authenticity."""
import hashlib
import html
import json
from pathlib import Path
import shutil

from ._tect.core import canonical
from ._tect.io import load
from .dossier import evaluate
from .researchos import assess


FILES = {'input.json', 'dossier.json', 'scenario.json', 'ledger.json',
         'researchos.json', 'review.html', 'manifest.json'}


def fingerprint():
    root = Path(__file__).parent
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*.py'))}


def contents(data):
    dossier = evaluate(data)
    scenario, ledger, report = assess(data, dossier)
    values = {name: canonical(value) for name, value in {
        'input.json': data, 'dossier.json': dossier, 'scenario.json': scenario,
        'ledger.json': ledger, 'researchos.json': report}.items()}
    values['review.html'] = ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Independent research dossier</title><style>body{font:16px system-ui;max-width:960px;margin:40px auto;padding:16px}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Independent research dossier</h1>'
        '<p>Independent concept, not affiliated with United Therapeutics. Research only; no clinical authority.</p>'
        '<h2>Evidence and research checks</h2><pre>' + html.escape(json.dumps(dossier, indent=2))
        + '</pre><h2>Captured research declarations</h2><pre>'
        + html.escape(json.dumps(data, indent=2, sort_keys=True))
        + '</pre><h2>ResearchOS assurance blockers</h2><pre>'
        + html.escape(json.dumps(report['assurance_blockers'], indent=2)) + '</pre></html>\n')
    values['manifest.json'] = canonical({'schema_version': 1, 'runtime': fingerprint(),
        'files': {name: hashlib.sha256(value.encode()).hexdigest() for name, value in values.items()}})
    if any(len(v.encode()) > 8*1024*1024 for v in values.values()):
        raise ValueError('Bundle file exceeds 8 MiB limit')
    return values


def write(data, output):
    values = contents(data)
    output = Path(output)
    output.mkdir()  # Existing results are never replaced.
    try:
        for name, value in values.items():
            (output/name).write_text(value, encoding='utf-8')
    except BaseException:
        shutil.rmtree(output)
        raise
    return json.loads(values['researchos.json'])


def verify(output):
    output = Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != FILES:
        raise ValueError('Invalid bundle file set')
    for name in FILES:
        path = output/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 8*1024*1024:
            raise ValueError('Expected bounded regular bundle files')
    expected = contents(load(output/'input.json'))
    for name, value in expected.items():
        if (output/name).read_bytes() != value.encode():
            raise ValueError('Recomputation mismatch: ' + name)
    return json.loads(expected['researchos.json'])
