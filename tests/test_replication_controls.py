import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pilots/02-gaming-viability/harness'))
import replication_controls as c
class Controls(unittest.TestCase):
    def test_sources_and_budget_carry(self):
        p,h,e,n=c.source_state();self.assertEqual(len(h),15);self.assertLess(e,2);self.assertLessEqual(n,2)
        for case in p['cases'][:15]:self.assertEqual(len(h[case['case']]['messages']),3)
if __name__=='__main__':unittest.main()
