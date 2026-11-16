#!/usr/bin/env python3
"""Reuse the frozen GAME-01 auditor with isolated scope/plan dependencies."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import llama_followup as f

g=f.g


def audit(root):
    # Load a separate auditor namespace: never change shared gaming globals or files.
    spec=importlib.util.spec_from_file_location('_llama_game_audit',g.HERE/'gaming_audit.py')
    auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)
    auditor.g=SimpleNamespace(**{**vars(g),'MODELS':f.MODELS,'verify_plan':f.verify_plan})
    result=auditor.audit(root)
    plan=f.verify_plan(root);manifest=g.old.load(Path(root)/'experiment/manifest.json')
    assert manifest['maximum_logical_calls']==plan['maximum_new_calls']==f.MAX_CALLS
    assert manifest['logical_calls_dispatched']<=f.MAX_CALLS
    assert set(c['candidate'] for c in manifest['candidates'])==set(f.MODELS)
    for candidate in manifest['candidates']:
        assert len(candidate['jobs'])==18
    result['checks']=[x.replace('exact reviewed game prompts','exact frozen implicit wording and original game prompts').replace('same pinned providers/settings except4096 cap','prefrozen Scout provider/fp8 preference; same non-thinking settings') for x in result['checks']]
    result['checks']+=['two fresh18-call graphs only; no historical reruns;36-call maximum']
    return result


if __name__=='__main__':
    root=Path(sys.argv[1]);result=audit(root)
    result['artifact_sha256']={str(p.relative_to(root)):g.s.sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='audit.json'}
    (root/'audit.json').write_text(g.s.dump(result)+'\n')
    print(g.s.dump({k:v for k,v in result.items() if k!='artifact_sha256'}))
