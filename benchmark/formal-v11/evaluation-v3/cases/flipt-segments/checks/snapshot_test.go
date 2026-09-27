package fs

import (
    "context"
    "fmt"
    "strings"
    "testing"
    "github.com/stretchr/testify/require"
    "go.flipt.io/flipt/rpc/flipt"
)

// task.md: rule segment decoding must also reach the filesystem snapshot.
func TestContractRuleSnapshotRepresentations(t *testing.T) {
    for _, tc := range []struct {name, segment string; keys []string; op flipt.SegmentOperator}{
        {"scalar", "s1", []string{"s1"}, flipt.SegmentOperator_OR_SEGMENT_OPERATOR},
        {"multi_and", "{keys: [s1, s2], operator: AND_SEGMENT_OPERATOR}", []string{"s1","s2"}, flipt.SegmentOperator_AND_SEGMENT_OPERATOR},
        {"multi_or", "{keys: [s1, s2], operator: OR_SEGMENT_OPERATOR}", []string{"s1","s2"}, flipt.SegmentOperator_OR_SEGMENT_OPERATOR},
    } {
        t.Run(tc.name, func(t *testing.T) {
            source := fmt.Sprintf(`namespace: default
flags:
- key: feature
  name: Feature
  enabled: true
  variants:
  - key: enabled
  rules:
  - segment: %s
    rank: 1
    distributions:
    - variant: enabled
      rollout: 100
segments:
- key: s1
  name: First
- key: s2
  name: Second
`, tc.segment)
            store, err := snapshotFromReaders(strings.NewReader(source))
            require.NoError(t, err)
            rules, err := store.GetEvaluationRules(context.Background(), "default", "feature")
            require.NoError(t, err)
            require.Len(t, rules, 1)
            require.Equal(t, tc.op, rules[0].SegmentOperator)
            require.Len(t, rules[0].Segments, len(tc.keys))
            // Keys are observable through the public stored Rule as well.
            rule, err := store.GetRule(context.Background(), "default", rules[0].ID)
            require.NoError(t, err)
            keys := rule.SegmentKeys
            if len(keys) == 0 && rule.SegmentKey != "" { keys = []string{rule.SegmentKey} }
            require.ElementsMatch(t, tc.keys, keys)
            require.Equal(t, tc.op, rule.SegmentOperator)
        })
    }
}
