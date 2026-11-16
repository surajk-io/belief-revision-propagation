import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1]/'pilots/02-gaming-viability/harness';sys.path.insert(0,str(HERE))
import robustness as f
import robustness_audit

def copied(root):
    root.mkdir()
    for p in f.ROOT.iterdir():
        if p.name in ('models-raw.json','discovery.json') or p.name.endswith('-endpoints.json'):shutil.copyfile(p,root/p.name)

class Robustness(unittest.TestCase):
    def test_scope_seeds_prompts(self):
        self.assertEqual(len(f.cases()),20);self.assertEqual(len({c['seed'] for c in f.cases()}),20)
        self.assertEqual(len(f.jobs()),420)
        self.assertEqual(sum(j['stage']==0 for j in f.jobs()),300)
        self.assertEqual(sum(j['condition']=='control' for j in f.jobs()),20)
        self.assertEqual(sum(j['base_id']=='initial' for j in f.jobs()),20)
        self.assertEqual(f.prompts()['initial'],f.g.prompts()['initial'])
        self.assertEqual(f.prompts()['U_15'],f.v.prompts()['U_15'])
    def test_full_fresh_graph_and_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'run';copied(root);f.freeze(root)
            with patch('sys.stdout',new=io.StringIO()):m=f.run(root,False)
            self.assertEqual(m['maximum_in_flight'],6)
            self.assertEqual(robustness_audit.audit(root)['status'],'passed')
            self.assertLessEqual(m['logical_calls_dispatched'],420)
            first=f.cases()[0];path=root/'experiment'/f.g.old.slug(first['candidate'])/first['case']
            rows=f.g.old.rows(path/'raw.jsonl')
            initial=next(r for r in rows if r['id'].endswith('__initial'))
            self.assertEqual(len(initial['request']['messages']),2)
            self.assertEqual(initial['request']['seed'],first['seed'])
            with self.assertRaises(FileExistsError):f.run(root,False)
    def test_bad_initial_is_retained_not_screened(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'run';copied(root);f.freeze(root)
            with patch('sys.stdout',new=io.StringIO()):m=f.run(root,False,{(f.REPLICATION[0],'h01__initial'):'length'})
            self.assertEqual(m['jobs']['h01']['h01__initial']['status'],'incomplete')
            self.assertEqual(m['jobs']['h01']['h01__W_15_A']['status'],'blocked_parent')
            self.assertEqual(m['jobs']['h02']['h02__W_15_A']['status'],'complete')
            self.assertEqual(robustness_audit.audit(root)['status'],'passed')
if __name__=='__main__':unittest.main()
