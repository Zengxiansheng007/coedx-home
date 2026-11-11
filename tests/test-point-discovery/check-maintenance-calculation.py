"""Scoped format/preservation checks. No natural-language semantic acceptance."""
from pathlib import Path
import hashlib
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills/test-point-discovery'
RUN = Path(__file__).parent / 'maintenance-calculation-run'


def read(path):
    return path.read_text(encoding='utf-8')


def module(text, name):
    return text.split(f'## {name}\n', 1)[1].split('\n## ', 1)[0].rstrip()


class ArtifactChecks(unittest.TestCase):
    def test_department_preserved_after_calculation_review(self):
        reviewed = read(RUN / 'department-d1.md')
        historical = read(RUN / 'v1-during-rejection.evidence.md')
        current = read(RUN / 'accurate.md')
        self.assertEqual(module(reviewed, '部门资料'), module(historical, '部门资料'))
        self.assertEqual(module(historical, '部门资料'), module(current, '部门资料'))

    def test_only_approved_calculation_version_in_current(self):
        current = read(RUN / 'accurate.md')
        self.assertEqual(module(read(RUN / 'calculation-d2.md'), '费用核算'),
                         module(current, '费用核算'))
        self.assertNotEqual(module(read(RUN / 'calculation-d1.md'), '费用核算'),
                            module(current, '费用核算'))

    def test_v1_at_rejection_matches_observed_identity(self):
        historical = read(RUN / 'v1-during-rejection.evidence.md')
        original = historical.split('\n<!-- Historical v1 evidence only; not current authority. -->')[0]
        # Text artifact is persisted through the governed Windows writer (CRLF).
        observed = hashlib.sha256(original.replace('\n', '\r\n').encode()).hexdigest()
        self.assertEqual(observed, '7c9fe4bd324b5b9ae3d844122ceaba7603b495e76e043575c1324a166cb7b67b')

    def test_tree_shape(self):
        for filename in ('department-d1.md', 'calculation-d1.md', 'calculation-d2.md', 'accurate.md'):
            text = read(RUN / filename)
            self.assertEqual(len(re.findall(r'^# ', text, re.M)), 1, filename)
            self.assertEqual(text.count('## 资料与Agent交接说明\n'), 1, filename)
            self.assertFalse(re.search(r'^#{7,} ', text, re.M), filename)

    def test_skill_local_references_resolve(self):
        for path in [SKILL / 'SKILL.md', *sorted((SKILL / 'references').glob('*.md'))]:
            for target in re.findall(r'\]\(([^)]+)\)', read(path)):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / target.split('#')[0]).is_file(), f'{path}: {target}')


if __name__ == '__main__':
    unittest.main()
