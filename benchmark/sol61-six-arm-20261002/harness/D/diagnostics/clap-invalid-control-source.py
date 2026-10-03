"""Symmetric native probe of existing occurrence behavior; no Actor rerun."""
from pathlib import Path
import json,subprocess,os,shutil,time,hashlib,re
import run
ROOT=run.ROOT/'diagnostics/clap-occurrences';ROOT.mkdir(parents=True,exist_ok=False)
plan=run.prepare();case=plan['cases']['clap-2297'];origin=run.CAL/'cases/clap-2297'
fixture=ROOT/'diagnostic_occurrences.rs'
fixture.write_text('''use clap::{App, Arg};
#[test]
fn diagnostic_preserve_occurrences() {
 for (kind,self_override,multi) in [("non_overriding_control",false,false),("self_override_single_value",true,false),("self_override_multi_values",true,true)] {
  let mut arg=Arg::new("input").long("input").takes_value(true).multiple_occurrences(true).multiple_values(multi);
  if self_override {arg=arg.overrides_with("input");}
  let tokens=if multi {vec!["app","--input","a","b","--input","c","d"]} else {vec!["app","--input","a","--input","c"]};
  let matches=App::new("app").arg(arg).get_matches_from(tokens);
  let values:Vec<_>=matches.values_of("input").unwrap().collect();
  println!("PROBE_RESULT {{\\"case\\":\\"{}\\",\\"occurrences\\":{},\\"values\\":{:?}}}",kind,matches.occurrences_of("input"),values);
 }
}
''',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',CARGO_BUILD_JOBS='1',RUSTFLAGS='-A warnings',CARGO_TARGET_DIR=str(run.CAL.parent/'round-10-evaluation-builds/clap-2297'))
for arm in ('BASE','A1','A2','B1','B2','D1','D2'):
 folder=ROOT/arm;folder.mkdir();work=(folder/'checkout').resolve();assert work.is_relative_to(ROOT.resolve())
 patch=None if arm=='BASE' else run.artifact('clap-2297',arm)/'final.patch'
 started=time.monotonic()
 def command(args,cwd=work,timeout=300):return subprocess.run([str(x) for x in args],cwd=cwd,env=env,capture_output=True,timeout=timeout)
 def must(args,cwd=work):
  p=command(args,cwd)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
  return p
 try:
  must(['git','-c','core.longpaths=true','-c','core.autocrlf=false','worktree','add','--detach',work,case['base_commit']],origin)
  assert must(['git','rev-parse','HEAD']).stdout.decode().strip()==case['base_commit']
  if patch:must(['git','apply','--whitespace=nowarn','--exclude=tests/*',patch])
  shutil.copy2(run.EVALUATION/'cases/clap-2297/Cargo.lock',work/'Cargo.lock')
  shutil.copy2(fixture,work/'tests/diagnostic_occurrences.rs')
  args=['cargo','test','--offline','--locked','-p','clap@3.0.0-beta.2','--test','diagnostic_occurrences','--','--nocapture','--test-threads=1']
  p=command(args);text=(p.stdout+p.stderr).decode(errors='replace');(folder/'cargo-test.txt').write_text(text,encoding='utf-8')
  probes=[json.loads(line[len('PROBE_RESULT '):]) for line in text.splitlines() if line.startswith('PROBE_RESULT ')]
  assert p.returncode==0 and len(probes)==3,text[-4000:]
  assert next(x for x in probes if x['case']=='non_overriding_control')['occurrences']==2
  row={'arm':arm,'base_commit':case['base_commit'],'patch_sha256':sha(patch) if patch else None,'fixture_sha256':sha(fixture),'exit_code':p.returncode,'seconds':time.monotonic()-started,'probes':probes,'offline_locked':True,'original_actor_scores_unchanged':True}
  (folder/'result.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');rows.append(row);print(json.dumps(row),flush=True)
 finally:
  if work.exists():
   assert work.name=='checkout' and work.is_relative_to(ROOT.resolve())
   p=command(['git','worktree','remove','--force',work],origin);assert p.returncode==0
baseline={p['case']:p['occurrences'] for p in rows[0]['probes']}
for row in rows:
 row['occurrences_preserved']=all(p['occurrences']==baseline[p['case']] for p in row['probes'])
(ROOT/'comparison.json').write_text(json.dumps({'task_clause':'Preserve existing argument validation, required/conflict rules, occurrences, defaults, and non-overriding parsing behavior.','baseline_occurrences':baseline,'rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'occurrences_preserved':{r['arm']:r['occurrences_preserved'] for r in rows}}),flush=True)
