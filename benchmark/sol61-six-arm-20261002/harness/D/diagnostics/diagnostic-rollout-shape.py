from pathlib import Path
import json,subprocess,hashlib,uuid,time,re
ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent.parent
plan=json.loads((STUDY/'plan.json').read_text())
case=plan['cases']['flipt-segments']
fixture=ROOT/'rollout_legacy_shape_audit_test.go'
fixture.write_text('''package ext
import (
 "bytes"
 "context"
 "encoding/json"
 "fmt"
 "testing"
 "go.flipt.io/flipt/rpc/flipt"
 "gopkg.in/yaml.v3"
)
func TestNudgeRolloutLegacyShapeAudit(t *testing.T) {
 for _,kind:=range []string{"scalar_key_control","single_list_key"} {
  t.Run(kind,func(t *testing.T){
   s:=&flipt.RolloutSegment{Value:true,SegmentOperator:flipt.SegmentOperator_OR_SEGMENT_OPERATOR}
   if kind=="scalar_key_control" { s.SegmentKey="internal_users" } else { s.SegmentKeys=[]string{"internal_users"} }
   lister:=mockLister{flags:[]*flipt.Flag{{Key:"flag2",Name:"flag2",Type:flipt.FlagType_BOOLEAN_FLAG_TYPE}},rollouts:[]*flipt.Rollout{{Id:"r1",FlagKey:"flag2",Type:flipt.RolloutType_SEGMENT_ROLLOUT_TYPE,Rule:&flipt.Rollout_Segment{Segment:s}}}}
   var b bytes.Buffer
   if err:=NewExporter(lister,flipt.DefaultNamespace).Export(context.Background(),&b);err!=nil {t.Fatal(err)}
   var doc map[string]interface{}
   if err:=yaml.Unmarshal(b.Bytes(),&doc);err!=nil {t.Fatal(err)}
   flags:=doc["flags"].([]interface{})
   rollouts:=flags[0].(map[string]interface{})["rollouts"].([]interface{})
   segment:=rollouts[0].(map[string]interface{})["segment"].(map[string]interface{})
   good:=segment["key"]=="internal_users" && segment["value"]==true && len(segment)==2
   payload,_:=json.Marshal(map[string]interface{}{"case":kind,"passed":good,"actual_segment":segment})
   fmt.Printf("PROBE_RESULT %s\\n",payload)
   if !good {t.Errorf("rollout must retain key/value shape; YAML: %s",b.String())}
  })
 }
}
''',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
def cmd(args,timeout=300):
 return subprocess.run(args,capture_output=True,timeout=timeout)
def must(args):
 p=cmd(args)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
 return p
roots={'A':Path('/mnt/e/masters-nudge-benchmark/sol61-ab-12case-20260930'),'B':Path('/mnt/e/masters-nudge-benchmark/sol61-b-finalized-12case-20261001'),'D':STUDY}
for arm in ('A1','A2','B1','B2','D1','D2'):
 output=ROOT/arm;output.mkdir(exist_ok=False)
 patch=roots[arm[0]]/'runs/flipt-segments'/arm/'final.patch';before=sha(patch)
 name='mn-diag-rollout-'+uuid.uuid4().hex[:12];started=time.monotonic()
 try:
  must(['docker','run','--detach','--pull=never','--network','none','--name',name,'--cpus','2','--memory','6g','--user','root','--entrypoint','sleep',case['image_id'],'infinity'])
  app='/app' if cmd(['docker','exec',name,'test','-d','/app']).returncode==0 else '/testbed'
  assert must(['docker','exec','--workdir',app,name,'git','rev-parse','HEAD']).stdout.decode().strip()==case['base_commit']
  must(['docker','cp',str(patch),name+':/tmp/delivery.patch'])
  exclusions=['test/*','tests/*','**/*_test.go','**/*.test.ts','**/*.test.tsx','**/*.spec.ts']
  must(['docker','exec','--workdir',app,name,'git','apply','--whitespace=nowarn',*['--exclude='+x for x in exclusions],'/tmp/delivery.patch'])
  must(['docker','cp',str(fixture),name+':'+app+'/internal/ext/rollout_legacy_shape_audit_test.go'])
  args=['docker','exec','--env','GOPROXY=off','--env','GOSUMDB=off','--workdir',app,name,'go','test','./internal/ext','-run','^TestNudgeRolloutLegacyShapeAudit$','-count=1','-v']
  p=cmd(args);text=(p.stdout+p.stderr).decode(errors='replace');(output/'go-test.txt').write_text(text)
  probes=[]
  for line in text.splitlines():
   if line.startswith('PROBE_RESULT '):probes.append(json.loads(line[len('PROBE_RESULT '):]))
  assert len(probes)==2 and next(x for x in probes if x['case']=='scalar_key_control')['passed'],text[-3000:]
  row={'arm':arm,'patch_sha256':before,'fixture_sha256':sha(fixture),'base_commit':case['base_commit'],'image_id':case['image_id'],'exit_code':p.returncode,'seconds':time.monotonic()-started,'probes':probes,'network':'none','original_actor_and_scores_unchanged':True}
  (output/'result.json').write_text(json.dumps(row,ensure_ascii=False,indent=2));rows.append(row)
  print(json.dumps(row,ensure_ascii=False),flush=True)
 finally:
  cmd(['docker','rm','--force',name]);assert sha(patch)==before
(ROOT/'comparison.json').write_text(json.dumps({'task_clause':'Rollout YAML keeps its existing segment: {key: <segmentKey>, value: <bool>} shape unchanged on import and export.','scope':'Diagnostic of an existing task clause raised by blind review; frozen scoring and Actors are untouched.','rows':rows},ensure_ascii=False,indent=2))
