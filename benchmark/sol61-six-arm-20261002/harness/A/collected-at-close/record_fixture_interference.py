"""Record external fixture interference without changing any Actor artifacts."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
folder=ROOT/'runs/nodebb-images/B1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
events=ROOT/'defender-fixture-events.json'
receipt={
    'case':'nodebb-images','arm':'B1',
    'classification':'external Windows Defender quarantine, not an observed Actor test edit',
    'fixture':'test/files/toobig.jpg',
    'defender_events_file':str(events),'defender_events_sha256':sha(events),
    'defender_detection_local':'2026-09-30T20:20:58.8905846+08:00',
    'defender_quarantine_local':'2026-09-30T20:21:29.1054776+08:00',
    'trigger_process':'rg.exe','action':'quarantine; successful',
    'transcript_sha256':sha(folder/'actor-events.jsonl'),
    'transcript_evidence_lines':[9,50,53,55,81],
    'result_sha256':sha(folder/'result.json'),'patch_sha256':sha(folder/'final.patch'),
    'legacy_harness_classification':'tests_modified; verification skipped',
    'recovery':'First fixed verification of the unchanged raw patch in the frozen container; original test paths already excluded by the sealed evaluator.',
    'actor_rerun':False,'actor_code_repair':False,'antivirus_configuration_change':False,
    'raw_artifacts_modified':False,
}
target=folder/'environment-interference.json'
assert not target.exists() or json.loads(target.read_text(encoding='utf-8'))==receipt
target.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
