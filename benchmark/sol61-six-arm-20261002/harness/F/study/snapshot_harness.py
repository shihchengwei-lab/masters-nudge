"""Exact inspectable study sources, unchanged dependencies and diagnostic fixtures."""
from pathlib import Path
import shutil,subprocess,json
import run
ROOT=run.ROOT;plan=run.prepare();entries=[]
def copy(source,relative):
 source=Path(source);target=ROOT/'harness-sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 entries.append({'source':str(source),'snapshot':target.relative_to(ROOT).as_posix(),'sha256':run.sha(source)})
for name in ('run.py','actor_runner.py','review.py','blind.py','finish.py','report.py','pipeline.py','preflight.py','verify_final.py','snapshot_harness.py','transcript_reader.py','diagnostic_clap_occurrences.py'):
 copy(ROOT/name,'study/'+name)
copy('E:/masters-nudge-benchmark/setup-f-xhigh-sol-20261002.py','study/setup-f-xhigh-sol.py')
copy(ROOT/'diagnostics/flipt-segments/run.py','diagnostics/flipt-original-clause.py')
copy(ROOT/'diagnostics/flipt-segments/rollout_legacy_shape_audit_test.go','diagnostics/rollout_legacy_shape_audit_test.go')
copy(ROOT/'diagnostics/clap-2297/diagnostic_occurrences.rs','diagnostics/diagnostic_occurrences.rs')
copy(run.SOURCE_HARNESS,'dependencies/original-actor-runner.py');copy(run.PREVIOUS/'rerun.py','dependencies/adapter.py');copy(run.CAL/'runner.py','dependencies/calibration-runner.py')
for p in sorted((run.CAL/'public-tools').glob('*.py')):copy(p,'public-tools/'+p.name)
copy('D:/masters-nudge-benchmark/selection/round-10/candidate-manifest.json','dependencies/candidate-manifest.json')
copy(run.CAL/'supplements/tracing-1523-public-layer-tests.rs','dependencies/tracing-1523-public-layer-tests.rs')
copy(run.PRODUCT/'benchmark/formal-v11/evaluation-v3/evaluate.py','dependencies/evaluate.py')
run.save(ROOT/'harness-source-manifest.json',entries)
p=subprocess.run(['git','diff','--no-index','--',str(run.E_REFERENCE/'actor_runner.py'),str(ROOT/'actor_runner.py')],capture_output=True);assert p.returncode in (0,1)
(ROOT/'actor-runner-from-E.patch').write_bytes(p.stdout)
print(json.dumps({'snapshot_count':len(entries),'references_C_E_preserved':True}))
