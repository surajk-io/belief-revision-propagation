import copy
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]/'pilots/01-viability/harness'
sys.path.insert(0,str(HERE))
import screen as x
import screen_audit
import smoke as s

DISCOVERY=s.PILOT/'screens/2026-11-16-b7da458-cross-model'


def endpoint(**changes):
    value={'tag':'test','provider_name':'Test','status':0,'service_tier':None,
           'supported_parameters':['max_tokens','temperature','top_p','seed'],
           'max_completion_tokens':1200,'pricing':{'prompt':'0.0000001','completion':'0.0000003'}}
    value.update(changes)
    return value


def selection():
    return x.select('test/model',{'test/model':{'canonical_slug':'test/model-v1'}},[endpoint()])


class Selection(unittest.TestCase):
    def test_unavailable_and_mandatory_reasoning_are_skipped(self):
        self.assertEqual(x.select('missing',{},[])['status'],'skip_unavailable')
        self.assertEqual(x.select('model',{'model':{'reasoning':{'mandatory':True}}},[endpoint()])['status'],'skip_incompatible')

    def test_explicit_reasoning_disable_and_unsupported_seed(self):
        ep=endpoint(supported_parameters=['max_tokens','temperature','top_p','reasoning'])
        value=x.select('model',{'model':{'reasoning':{'mandatory':False}}},[ep])
        self.assertEqual(value['parameters']['reasoning'],{'enabled':False,'exclude':True})
        self.assertNotIn('seed',value['parameters'])
        self.assertEqual(value['unsupported_settings'],['seed'])
        incompatible=x.select('model',{'model':{'reasoning':{'mandatory':False}}},[endpoint()])
        self.assertEqual(incompatible['status'],'skip_incompatible')

    def test_selection_prefers_supported_seed_and_standard_availability(self):
        candidates=[endpoint(tag='cheap-no-seed',supported_parameters=['max_tokens','temperature','top_p'],pricing={'prompt':'0.000000001','completion':'0.000000001'}),
                    endpoint(tag='seed'),endpoint(tag='flex',service_tier='flex'),endpoint(tag='failed',status=-2)]
        value=x.select('model',{'model':{}},candidates)
        self.assertEqual(value['endpoint_tag'],'seed')
        self.assertNotIn('reasoning',value['parameters'])
        self.assertEqual(len(value['exclusions']),2)


class TransportAndBudget(unittest.TestCase):
    def test_shared_budget_is_not_reset_between_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifacts=s.Artifacts(Path(tmp)/'batch')
            cfg=s.config();cfg['budget_usd']='0.015'
            budget=x.SharedBudget(artifacts,cfg)
            a=x.ScreenClient(s.Artifacts(Path(tmp)/'a'),cfg,False,selection(),budget)
            b=x.ScreenClient(s.Artifacts(Path(tmp)/'b'),cfg,False,selection(),budget)
            with patch('sys.stdout',new=io.StringIO()):
                a.call('initial',[],'question',None,'A')
                with self.assertRaisesRegex(RuntimeError,'Budget reservation'):
                    b.call('initial',[],'question',None,'A')
            self.assertEqual(budget.attempts,1)
            self.assertEqual(len(x.rows(artifacts.path/'ledger.jsonl')),1)

    def test_real_transport_records_and_rejects_reasoning_without_saving_trace(self):
        class Response:
            status=200;headers={}
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self):return json.dumps({'id':'test','model':'test/model','provider':'Test',
                'choices':[{'message':{'role':'assistant','content':'The risk estimate is 11.7%.','reasoning':'HIDDEN_TRACE'},'finish_reason':'stop'}],
                'usage':{'prompt_tokens':30,'completion_tokens':10,'cost':0.00001,'completion_tokens_details':{'reasoning_tokens':1}}}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            a=s.Artifacts(Path(tmp)/'batch','TEST_KEY')
            cfg=s.config();budget=x.SharedBudget(a,cfg)
            client=x.ScreenClient(s.Artifacts(Path(tmp)/'model','TEST_KEY'),cfg,True,selection(),budget)
            with patch.object(client.opener,'open',return_value=Response()),patch('sys.stdout',new=io.StringIO()):
                with self.assertRaisesRegex(RuntimeError,'Non-reasoning configuration'):
                    client.call('initial',[],'question',None,'A')
            raw=(client.a.path/'raw.jsonl').read_text()
            self.assertNotIn('HIDDEN_TRACE',raw)
            self.assertNotIn('TEST_KEY',raw)
            self.assertTrue(x.rows(client.a.path/'raw.jsonl')[0]['hidden_trace_present'])
            request=x.rows(client.a.path/'requests.jsonl')[0]['request']
            self.assertEqual(request['provider']['only'],['test'])
            self.assertFalse(request['provider']['allow_fallbacks'])


class Screens(unittest.TestCase):
    def test_all_fixed_graphs_two_budgets_and_batch_order(self):
        previous={str(p):x.inventory(p) for p in (s.PILOT/'runs').iterdir() if p.is_dir()}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'screen';root.mkdir()
            for p in DISCOVERY.iterdir():
                if p.name=='models-raw.json' or p.name.endswith('-endpoints.json'):
                    shutil.copyfile(p,root/p.name)
            plan=x.freeze(root)
            self.assertEqual(len(plan['choices']['1']),3)
            self.assertEqual(len(plan['choices']['2']),4)
            with self.assertRaisesRegex(RuntimeError,'Batch 1 must finish'):
                x.run_batch(root,2,False)
            with patch('sys.stdout',new=io.StringIO()):
                first=x.run_batch(root,1,False)
            audit1=screen_audit.audit(root,1)
            (root/'batch-1/audit.json').write_text(s.dump(audit1)+'\n')
            with patch('sys.stdout',new=io.StringIO()):
                second=x.run_batch(root,2,False)
            audit2=screen_audit.audit(root,2)
            self.assertEqual(first['logical_calls'],54)
            self.assertEqual(second['logical_calls'],72)
            self.assertLessEqual(float(first['reserved_usd']),1)
            self.assertLessEqual(float(second['reserved_usd']),1)
            self.assertEqual(audit1['status'],'passed')
            self.assertEqual(audit2['status'],'passed')
            self.assertEqual(previous,{str(p):x.inventory(p) for p in (s.PILOT/'runs').iterdir() if p.is_dir()})
            with self.assertRaises(FileExistsError):x.run_batch(root,1,False)
            model=root/'batch-2'/x.slug(x.BATCHES[2][1])
            requests=x.rows(model/'requests.jsonl')
            requests[1]['request']['messages'].insert(-1,s.message('assistant','Sibling leak'))
            (model/'requests.jsonl').write_text('\n'.join(json.dumps(v) for v in requests))
            with self.assertRaises(AssertionError):screen_audit.audit(root,2)


if __name__=='__main__':unittest.main()
