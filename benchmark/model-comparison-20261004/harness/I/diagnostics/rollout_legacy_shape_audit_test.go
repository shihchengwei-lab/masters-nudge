package ext
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
   fmt.Printf("PROBE_RESULT %s\n",payload)
   if !good {t.Errorf("rollout must retain key/value shape; YAML: %s",b.String())}
  })
 }
}
