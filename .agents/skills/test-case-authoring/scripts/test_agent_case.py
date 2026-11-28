"""Retrieve one executable case through the delivered Agent index."""
import json
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from authoring import _digest
from test_scoped_review import catalog


class AgentCaseTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.scripts = Path(__file__).resolve().parent
        self.full = catalog()
        for case in self.full['cases']:
            step = case['steps'][0]
            step['expected'] = case['steps'][1]['expected']
            step['verification'] = case['steps'][1]['verification']
        self.version = _digest({k: v for k, v in self.full.items() if k != 'content_version'})
        self.full['content_version'] = self.version
        self.save('full.json', self.full)

    def save(self, name, value):
        (self.root / name).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')

    def read(self, name):
        return json.loads((self.root / name).read_text(encoding='utf-8'))

    def cli(self, script, *args, check=True):
        return subprocess.run([sys.executable, str(self.scripts / script), *args], cwd=self.root,
                              check=check, capture_output=True, text=True, encoding='utf-8')

    def export_draft(self):
        self.cli('source_preparation.py', '--candidate', 'full.json', '--case', 'EDIT',
                 '--output-dir', 'draft')

    def extract(self, directory='draft', *, case='EDIT', version=None, check=True):
        return self.cli('single_case.py', '--agent', directory + '/agent.json', '--version',
                        version or self.version, '--case', case, '--output', 'one.json', check=check)

    def test_draft_agent_delivers_only_the_requested_case_with_current_values(self):
        self.export_draft()
        self.extract()
        packet = self.read('one.json')
        self.assertEqual(packet['case']['id'], 'EDIT')
        self.assertEqual(packet['content_version'], self.version)
        self.assertEqual(packet['case']['context']['role'][0]['text'], 'editor')
        self.assertEqual(packet['case']['steps'], self.full['cases'][0]['steps'])
        self.assertEqual(packet['data']['title']['value'], 'Sample notice')
        self.assertEqual(packet['endpoint']['step_id'], packet['case']['steps'][-1]['id'])

    def test_draft_scope_and_versioned_identity_must_match_the_materialized_index(self):
        self.export_draft()
        self.assertNotEqual(self.extract(case='LINK', check=False).returncode, 0)
        index = self.read('draft/agent.json')
        for field, replacement in [('format', 'another format'), ('content_version', 'stale'),
                                   ('candidate', '../full.json'), ('case_ids', ['EDIT', 'LINK']),
                                   ('case_ids', ['EDIT', 'EDIT'])]:
            with self.subTest(field=field, replacement=replacement):
                self.save('draft/agent.json', dict(index, **{field: replacement}))
                self.assertNotEqual(self.extract(check=False).returncode, 0)
        for field, replacement in [('steps', {}), ('data_refs', ['no-such-input'])]:
            changed = copy.deepcopy(index)
            changed['cases']['EDIT'][field] = replacement
            self.save('draft/agent.json', changed)
            self.assertNotEqual(self.extract(check=False).returncode, 0)
        self.assertFalse((self.root / 'one.json').exists())

    def test_partial_delivery_resolves_only_its_bound_parent_and_never_selects_a_parent_case(self):
        self.save('request.json', dict(batch_id='for execution', review_layout='incremental-v1',
                                       selection=[dict(case_id='EDIT', action='reuse', reason='review')]))
        self.cli('scoped_review.py', '--catalog', 'full.json', '--request', 'request.json',
                 '--output-dir', 'partial')
        index = self.read('partial/agent.json')
        version = index['content_version']
        self.extract('partial', version=version)
        self.assertEqual(self.read('one.json')['content_version'], version)
        (self.root / 'one.json').unlink()
        self.assertNotEqual(self.extract('partial', case='LINK', version=version, check=False).returncode, 0)
        for field, replacement in [('source_catalog_version', 'stale'), ('source_catalog', '../full.json')]:
            self.save('partial/agent.json', dict(index, **{field: replacement}))
            self.assertNotEqual(self.extract('partial', version=version, check=False).returncode, 0)
        self.save('partial/agent.json', index)
        parent = self.read('partial/source-catalog.json')
        parent['cases'][1]['title'] = 'changed outside the selected scope'
        self.save('partial/source-catalog.json', parent)
        self.assertNotEqual(self.extract('partial', version=version, check=False).returncode, 0)
        self.assertFalse((self.root / 'one.json').exists())

    def test_an_unbound_parent_cannot_supply_missing_source_data(self):
        self.export_draft()
        index = self.read('draft/agent.json')
        self.save('draft/agent.json', dict(index, source_catalog='source-catalog.json',
                                           source_catalog_version=self.version))
        self.save('draft/source-catalog.json', self.full)
        self.assertNotEqual(self.extract(check=False).returncode, 0)
        self.assertFalse((self.root / 'one.json').exists())
