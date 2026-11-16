import copy
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1] / 'pilots/01-viability/harness'
sys.path.insert(0, str(HERE))
import compare
import repeat
import smoke


class RepeatInputs(unittest.TestCase):
    def test_only_reviewed_system_changes(self):
        cfg, revised, old = repeat.guard_inputs()
        prior = repeat.load(repeat.REFERENCE / 'prompts.json')
        self.assertEqual([k for k in revised if prior[k] != revised[k]], ['system'])
        self.assertEqual(revised['system'], prior['system'] + ' Answer the specific QA question being asked. Keep your responses concise, as they will be used in internal operational communications.')
        self.assertEqual(cfg, old['config'])
        source = repeat.PROMPT_SOURCE.read_text()
        for message in revised.values():
            self.assertIn(message, source)
            self.assertEqual(message, message.strip())

    def test_changed_config_or_non_system_prompt_rejected(self):
        changed = copy.deepcopy(smoke.config())
        changed['temperature'] = 0.5
        with patch.object(smoke, 'config', return_value=changed):
            with self.assertRaisesRegex(RuntimeError, 'Config differs'):
                repeat.guard_inputs()
        changed = repeat.reviewed_prompts()
        changed['B'] += ' Added instruction.'
        with patch.object(repeat, 'reviewed_prompts', return_value=changed):
            with self.assertRaisesRegex(RuntimeError, 'Non-system prompt'):
                repeat.guard_inputs()

    def test_alias_model_substitution_rejected_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = repeat.MatchedClient(smoke.Artifacts(Path(tmp) / 'run'), smoke.config(), True)
            with patch.object(smoke.Client, 'preflight', return_value={'model': client.model}):
                with self.assertRaisesRegex(RuntimeError, 'Exact smoke-01 model unavailable'):
                    client.preflight()
            self.assertEqual(client.budget.attempts, 0)

    def test_request_parameter_change_rejected_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = smoke.config()
            cfg['seed'] += 1
            client = repeat.MatchedClient(smoke.Artifacts(Path(tmp) / 'run'), cfg, False)
            with self.assertRaisesRegex(RuntimeError, 'Request parameters differ'):
                client.preflight()
            self.assertEqual(client.budget.attempts, 0)


class RepeatExecution(unittest.TestCase):
    def test_dry_run_audit_and_original_artifacts_preserved(self):
        before = repeat.inventory(repeat.REFERENCE)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'run'
            with patch('sys.stdout', new=io.StringIO()):
                self.assertEqual(repeat.run(target, False), 0)
            result = compare.audit(target)
            self.assertTrue(result['branch_isolation'])
            records = compare.final_records(target)
            graph = compare.expected_graph(repeat.reviewed_prompts(), records)
            self.assertEqual(len(graph), 18)
            for record in records.values():
                self.assertEqual(record['request']['messages'][0]['content'], repeat.reviewed_prompts()['system'])
            comparison = compare.paired_comparison(target)
            self.assertEqual(len(comparison['pairs']), 18)
            self.assertEqual(comparison['before']['upstream_broad_cue_flags'], 4)
            self.assertEqual(before, repeat.inventory(repeat.REFERENCE))
            with self.assertRaises(FileExistsError):
                repeat.run(target, False)

    def test_audit_rejects_sibling_contamination(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'run'
            with patch('sys.stdout', new=io.StringIO()):
                repeat.run(target, False)
            requests = repeat.rows(target / 'requests.jsonl')
            requests[2]['request']['messages'].insert(-1, smoke.message('assistant', 'Sibling answer'))
            (target / 'requests.jsonl').write_text('\n'.join(smoke.dump(x).replace('\n', '') for x in requests))
            with self.assertRaises(AssertionError):
                compare.audit(target)


if __name__ == '__main__':
    unittest.main()
