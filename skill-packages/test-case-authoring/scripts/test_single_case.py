import unittest
from authoring import build_batch
from test_authoring import sample
from single_case import get_case


class IndependentCaseTests(unittest.TestCase):
    def test_independent_case_matches_current_steps_and_data(self):
        recording, draft = sample()
        observed = dict(text='Title is visible', source='recording', lines=[2, 2])
        draft['steps'][0].update(expected=[observed], verification=[observed])
        batch = build_batch(recording, draft)['batch']
        case = batch['cases'][0]
        record = get_case(batch, batch['content_version'], case['id'])
        self.assertEqual(record['case']['steps'], case['steps'])
        self.assertEqual(record['endpoint']['step_id'], case['steps'][-1]['id'])
        self.assertEqual(record['case']['execution_status'], 'not_run')
        with self.assertRaisesRegex(ValueError, 'version'):
            get_case(batch, 'previous', case['id'])

    def test_named_chat_contains_exact_input_and_applicable_instruction(self):
        from source_preparation import assess_preparations
        from presentation import render_chat
        recording, draft = sample()
        draft['data'][0]['value'] = {'params': {}}
        observed = dict(text='Title is visible', source='recording', lines=[2, 2])
        draft['steps'][0].update(expected=[observed], verification=[observed])
        batch = build_batch(recording, draft)['batch']
        case = batch['cases'][0]
        definition = dict(name='现场窗口', instruction='开窗记时', timing='填入前',
                          source='source lines 1-2', module_path=case['module_path'],
                          applicable={case['id']: ['steps/' + case['steps'][0]['id']]},
                          excluded={}, pending={}, kind='evidence')
        batch = assess_preparations(batch, [definition])
        chat = render_chat(batch, [case['id']])['human_view']
        for value in ('开窗记时', '"params": {}', 'Title is visible', 'Read the visible saved message'):
            self.assertIn(value, chat)

    def test_duplicate_step_identity_is_not_a_unique_endpoint(self):
        from authoring import _digest
        recording, draft = sample()
        draft['steps'][0].update(expected=draft['steps'][1]['expected'], verification=draft['steps'][1]['verification'])
        batch = build_batch(recording, draft)['batch']
        case = batch['cases'][0]
        case['steps'][1]['id'] = case['steps'][0]['id']
        batch['content_version'] = _digest({k: v for k, v in batch.items() if k != 'content_version'})
        with self.assertRaisesRegex(ValueError, 'step identity'):
            get_case(batch, batch['content_version'], case['id'])

    def test_partial_copy_requires_the_exact_parent(self):
        from authoring import _digest
        from scoped_review import build_scoped_review
        from test_scoped_review import catalog
        full = catalog()
        for case in full['cases']:
            case['steps'][0]['expected'] = case['steps'][1]['expected']
            case['steps'][0]['verification'] = case['steps'][1]['verification']
        subset = build_scoped_review(full, 'one', [
            dict(case_id='EDIT', action='related', reason='scope')])['batch']
        version = subset['content_version']
        with self.assertRaisesRegex(ValueError, 'complete parent'):
            get_case(subset, version, 'EDIT')
        self.assertEqual(get_case(subset, version, 'EDIT', source_catalog=full)['case']['id'], 'EDIT')
        wrong_parent = dict(full, cases=list(reversed(full['cases'])))
        with self.assertRaisesRegex(ValueError, 'complete parent'):
            get_case(subset, version, 'EDIT', source_catalog=wrong_parent)
        subset['data'].append(subset['data'][0])
        subset['content_version'] = _digest({k: v for k, v in subset.items() if k != 'content_version'})
        with self.assertRaisesRegex(ValueError, 'Data title'):
            get_case(subset, subset['content_version'], 'EDIT', source_catalog=full)

    def test_every_claim_has_nonblank_business_text(self):
        from authoring import _digest
        recording, draft = sample()
        ok = [{"text": "observed", "source": "recording", "lines": [2, 2]}]
        draft["steps"][0].update(expected=ok, verification=ok)
        batch = build_batch(recording, draft)["batch"]
        case = batch["cases"][0]
        step = case["steps"][0]
        for field in ("expected", "verification"):
            for bad in ([], [{}], [{"text": " "}], "plain text", [None], [{"text": 123}]):
                with self.subTest(field=field, bad=bad):
                    step[field] = bad
                    batch["content_version"] = _digest({k: v for k, v in batch.items() if k != "content_version"})
                    with self.assertRaisesRegex(ValueError, f"{case['id']}/steps/{step['id']}:.*{field}"):
                        get_case(batch, batch["content_version"], case["id"])
            step[field] = ok
