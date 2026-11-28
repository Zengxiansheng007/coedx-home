"""Check the two delivered reader artifacts at their three public CLI boundaries."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from authoring import _digest
from test_handwritten import handwritten_sample
from test_scoped_review import catalog


class ReaderDeliveryTests(unittest.TestCase):
    def test_full_draft_and_premerge_share_version_and_selected_case_ids(self):
        scripts = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def save(name, value):
                (root / name).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
            def run(script, *args):
                subprocess.run([sys.executable, str(scripts / script), *args], cwd=root, check=True)
            def inspect(directory, stage, ids):
                delivery = root / directory
                agent = json.loads((delivery / 'agent.json').read_text(encoding='utf-8'))
                candidate = json.loads((delivery / agent['candidate']).read_text(encoding='utf-8'))
                review = (delivery / 'xmind.md').read_text(encoding='utf-8')
                self.assertEqual((agent['stage'], agent['case_ids']), (stage, ids))
                self.assertEqual(agent['content_version'], candidate['content_version'])
                self.assertIn(agent['content_version'], review)
                for cid in ids:
                    self.assertIn(cid, review)
                return agent, review, candidate
            handwritten, interpretation = handwritten_sample()
            (root / 'handwritten.md').write_text(handwritten, encoding='utf-8')
            save('draft.json', interpretation)
            run('authoring.py', '--handwritten', 'handwritten.md', '--interpretation', 'draft.json',
                '--output-dir', 'full')
            inspect('full', 'full', [interpretation['case_id']])
            full = catalog()
            full['data'][0].update(validity='execution window', reuse_policy='private fixture policy',
                                    invalidation_action='replace invalid fixture')
            full['content_version'] = _digest({k: v for k, v in full.items() if k != 'content_version'})
            save('catalog.json', full)
            ids = ['LINK', 'EDIT']
            run('source_preparation.py', '--candidate', 'catalog.json', '--case', ids[0], '--case', ids[1],
                '--output-dir', 'draft')
            agent, review, candidate = inspect('draft', 'draft', ids)
            self.assertNotIn('private fixture policy', review)
            self.assertEqual(candidate['data'][0]['reuse_policy'], 'private fixture policy')
            save('request.json', dict(batch_id='premerge', review_layout='incremental-v1',
                selection=[dict(case_id=ids[0], action='reuse', reason='review')]))
            run('scoped_review.py', '--catalog', 'catalog.json', '--request', 'request.json',
                '--output-dir', 'premerge')
            agent, review, scoped = inspect('premerge', 'premerge', ids[:1])
            from feedback import prepare_feedback
            confirmation = prepare_feedback(scoped, 'markdown', markdown=review,
                companion_base=root / 'premerge', source_catalog=full, actual_reply='Reviewed scope unchanged')
            self.assertEqual(confirmation['changes'], [])
            self.assertNotIn('private fixture policy', review)
            self.assertEqual(json.loads((root / 'premerge' / agent['source_catalog']).read_text(encoding='utf-8')), full)
