"""Verify private frozen desktop CLI and preserved startup evidence; no global install."""
from pathlib import Path
import json,hashlib,subprocess
root=Path(__file__).resolve().parent
receipt=json.loads((root/'binary-recovery.json').read_text())
for name,digest in receipt['files'].items():
 assert hashlib.sha256((root/'frozen-cli'/name).read_bytes()).hexdigest()==digest
assert subprocess.check_output([receipt['binary'],'--version'],text=True).strip()==receipt['version']
for probe in receipt['startup_probes'].values():assert probe['ready'] and probe['exit_code']==0
assert hashlib.sha256((Path(receipt['startup_failure_root'])/'STARTUP-FAILURE.json').read_bytes()).hexdigest()==receipt['startup_failure_receipt_sha256']
print('Frozen desktop CLI and successful model probes verified.')
