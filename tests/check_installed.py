"""Run after pip install .; subprocesses import outside the source checkout."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    run = Path(tmp)/'run'
    args = [sys.executable, '-I', '-m', 'therapeutics_research']
    first = subprocess.run(args + ['analyze', str(root/'examples/dossier.json'), '--output', str(run)],
                           cwd=tmp, capture_output=True, text=True, check=True)
    assert json.loads(first.stdout)['status'] == 'COMPUTED_UNASSURED'
    second = subprocess.run(args + ['verify', str(run)], cwd=tmp, capture_output=True, text=True, check=True)
    assert json.loads(second.stdout)['status'] == 'REPLAY_CONSISTENT_UNASSURED'
    duplicate = subprocess.run(args + ['analyze', str(root/'examples/dossier.json'), '--output', str(run)],
                               cwd=tmp, capture_output=True, text=True)
    assert duplicate.returncode == 2
    (run/'dossier.json').write_text('{}')
    tampered = subprocess.run(args + ['verify', str(run)], cwd=tmp, capture_output=True, text=True)
    assert tampered.returncode == 2
print('Installed analyze/replay, overwrite rejection and tamper rejection passed')
