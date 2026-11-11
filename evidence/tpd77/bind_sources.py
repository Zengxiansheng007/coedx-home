"""Derive R2 from frozen R1 identities; never recapture immutable evidence."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/tpd77'
R1_COMMIT = 'bd80c29b0cf426bbe930f7a5069fcd1b5b8b332a'
ADMIN = ('dev', 'context/development-status.md')


def task_root(root):
    candidates = []
    for candidate in (root.parent, root.parents[1]):
        marker = candidate / 'context/source-bindings.json'
        if marker.is_file():
            data = json.loads(marker.read_text(encoding='utf-8'))
            if (data.get('source_head') == 'f74938f64c683f3baa1cabdb37cead6f0e9e2929'
                    and data.get('mode') == 'implement-spec standalone; no develop-system run activated'
                    and data.get('requirements', {}).get('core-v0.6') ==
                    'AF4179AC42809C4006A52A781477D758543D44BC02291FF253B4B1333F910FB3'):
                candidates.append(candidate)
    if len(candidates) != 1:
        raise RuntimeError('Expected exactly one TPD task root marker; found: ' + str(candidates))
    return candidates[0]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def main():
    task_root(ROOT)
    raw = (OUT / 'source-bindings.json').read_bytes()
    if raw != git('show', R1_COMMIT + ':evidence/tpd77/source-bindings.json'):
        raise RuntimeError('R1 capture differs from frozen Git original')
    result = json.loads(raw)
    admin = [r for r in result['evidence'] if (r['area'], r['path']) == ADMIN]
    if len(result['evidence']) != 288 or len(admin) != 1:
        raise RuntimeError('Unexpected R1 evidence scope')
    result['evidence'] = [r for r in result['evidence'] if (r['area'], r['path']) != ADMIN]
    result['administrative_capture'] = {
        'record': admin[0],
        'scope': 'Historical R1 capture only; appendable status is excluded from current immutable validation.'}
    result['revision'] = 'R2'
    result['r1_capture'] = {'commit': R1_COMMIT, 'path': 'evidence/tpd77/source-bindings.json',
                            'sha256': hashlib.sha256(raw).hexdigest(), 'evidence_files': 288}
    result['scope'] = '287 original immutable R1 identities, unchanged; one historical administrative capture excluded; not semantic validation'
    source = result['source_commit']
    if (git('rev-parse', source + ':skills/test-point-discovery') !=
            git('rev-parse', 'HEAD:skills/test-point-discovery')
            or git('diff', source, '--', 'skills/test-point-discovery')):
        raise RuntimeError('Product source drift')
    (OUT / 'source-bindings-r2.json').write_bytes(
        (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'revision': 'R2', 'immutable_evidence_files': 287,
                      'historical_administrative_captures': 1, 'r1_preserved': True}))


if __name__ == '__main__':
    main()
