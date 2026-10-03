"""Save exact study and dependency source files for reader inspection."""
from pathlib import Path
import shutil,json,hashlib,subprocess
import run
ROOT=run.ROOT;plan=run.prepare();OUT=ROOT/'harness-sources';OUT.mkdir(exist_ok=True)
entries=[]
def copy(source,relative,key=None):
 source=Path(source);target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(source,target)
 row={'source':str(source),'snapshot':target.relative_to(ROOT).as_posix(),'sha256':run.sha(target)}
 if key:assert row['sha256']==plan[key];row['plan_hash_key']=key
 entries.append(row)
for name in ['run.py','actor_runner.py','finish.py','review.py','blind.py','preflight.py','pipeline.py','verify_final.py','snapshot_harness.py','transcript_reader.py','recover_cli.py']:
 copy(ROOT/name,'study/'+name)
copy('E:/masters-nudge-benchmark/setup-d-astra-provider-20261001.py','study/setup-d-astra-provider.py')
copy('E:/masters-nudge-benchmark/setup-d-desktop-recovery-20261001.py','study/setup-d-desktop-recovery.py')
copy(run.SOURCE_HARNESS,'dependencies/original-actor-runner.py','source_harness_sha256')
copy(run.PREVIOUS/'rerun.py','dependencies/adapter.py','adapter_sha256')
copy(run.CAL/'runner.py','dependencies/calibration-runner.py')
for p in sorted((run.CAL/'public-tools').glob('*.py')):copy(p,'public-tools/'+p.name)
copy('D:/masters-nudge-benchmark/selection/round-10/candidate-manifest.json','dependencies/candidate-manifest.json')
copy(run.CAL/'supplements/tracing-1523-public-layer-tests.rs','dependencies/tracing-1523-public-layer-tests.rs')
copy(run.PRODUCT/'benchmark/formal-v11/evaluation-v3/evaluate.py','dependencies/evaluate.py')
assert run.sha(run.PRODUCT/'benchmark/formal-v11/evaluation-v3/evaluate.py')==run.sha(run.EVALUATION/'evaluate.py')
run.save(ROOT/'harness-source-manifest.json',entries)
p=subprocess.run(['git','diff','--no-index','--',str(run.SOURCE_HARNESS),str(run.HARNESS)],capture_output=True)
assert p.returncode in (0,1)
(ROOT/'actor-runner-source-diff.patch').write_bytes(p.stdout)
print(json.dumps({'snapshot_count':len(entries),'frozen_source_dependencies_match':True}))
