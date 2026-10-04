from pathlib import Path
import shutil,json,hashlib,subprocess,ast
old=Path('E:/masters-nudge-benchmark/sol61-astra-provider-12case-20261001')
root=Path('E:/masters-nudge-benchmark/sol61-astra-provider-12case-20261001-desktop')
assert not root.exists();root.mkdir()
for name in ('run.py','actor_runner.py','review.py','blind.py','pipeline.py','finish.py','preflight.py','snapshot_harness.py','verify_final.py','transcript_reader.py','MATERIALS.zh-TW.md'):
 shutil.copy2(old/name,root/name)
for name in ('frozen-plugin','frozen-evaluation','prompts'):shutil.copytree(old/name,root/name)
source=Path('C:/Users/kk789/AppData/Local/OpenAI/Codex/bin/de8a38d2100ae498')
shutil.copytree(source,root/'frozen-cli')
binary=root/'frozen-cli/codex.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(binary)=='34549ded6e2aee87c911c62d025e52e26c488683d0f489cd68f756baef1a6df6'
receipt={'source':'installed Codex desktop executable directory','source_directory':str(source),'binary':str(binary),'binary_sha256':sha(binary),'expected_archived_binary_sha256':'86e8ef1013f98df51fdeea446597f7e3ca32e454d1d4d8c0402a68b03c311d70','version':'codex-cli 0.159.2','exact_binary_match':False,'user_choice':'Use tested desktop 0.159.2 and disclose version/hash difference; archived B not rerun.','files':{p.name:sha(p) for p in (root/'frozen-cli').iterdir() if p.is_file()},'startup_probes':{m:json.loads((old/'startup-probes'/m/'receipt.json').read_text()) for m in ('gpt-6.1-sol','gpt-6-astra')},'startup_failure_root':str(old),'startup_failure_receipt_sha256':sha(old/'STARTUP-FAILURE.json')}
assert subprocess.check_output([str(binary),'--version'],text=True).strip()==receipt['version']
(root/'binary-recovery.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
(root/'recover_cli.py').write_text('''"""Verify private frozen desktop CLI and preserved startup evidence; no global install."""
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
''',encoding='utf-8')
p=root/'run.py';s=p.read_text();s=s.replace('21f6fb0b01ba12a687f5fcd33546c0008ebd45654fdb23d84732ee8d62ee980b',receipt['binary_sha256']).replace('codex-cli 0.158.0-alpha.2.1','codex-cli 0.159.2').replace("'codex_cli_version':'0.158.0-alpha.2.1'","'codex_cli_version':'0.159.2'").replace('Use official same-version package and disclose different binary hash; no B rerun.','Use tested desktop 0.159.2 and disclose version/hash difference; no B rerun.').replace('Same CLI version recovered from official npm has a different binary hash from archived desktop build, explicitly accepted and disclosed.','Desktop CLI 0.159.2 differs in version and binary hash from archived 0.158.0-alpha.2.1, explicitly accepted and disclosed.').replace('disclosed same-version CLI binary difference','disclosed CLI version and binary difference');p.write_text(s,encoding='utf-8',newline='\n')
p=root/'finish.py';s=p.read_text();s=s.replace('基底、CLI版本、固定工具prompt','基底、固定工具prompt').replace('本輪經使用者同意改用官方npm發布的同版本0.158.0-alpha.2.1；二進位SHA256不同。','官方npm舊版無法啟動Sol，本輪經使用者同意改用已驗證的桌面CLI 0.159.2；與封存B的0.158.0-alpha.2.1相比，版本及SHA256均不同。').replace('原始來源與指紋見binary-recovery.json及plan.json。','原始來源、模型啟動檢查與指紋見binary-recovery.json及plan.json；舊版啟動失敗兩份尚未解題，另保留於'+str(old).replace('\\','/')+'，不計為本輪解題樣本。');p.write_text(s,encoding='utf-8',newline='\n')
p=root/'MATERIALS.zh-TW.md';s=p.read_text();s=s.replace('本輪經使用者同意，使用官方npm發布的同版本0.158.0-alpha.2.1，平台包SHA512已驗證。','官方npm同版本0.158.0-alpha.2.1被服務端拒絕使用Sol；流程在兩次啟動失敗後自動停止，零解題、零Provider、12題還原。使用者進一步同意本輪改用已驗證可正常呼叫兩模型的桌面CLI 0.159.2。啟動失敗完整紀錄保留於'+str(old).replace('\\','/')+'，不計入正式24份。').replace('它與封存B的桌面二進位SHA256不同','它與封存B的CLI版本及SHA256均不同').replace('21f6fb0b01ba12a687f5fcd33546c0008ebd45654fdb23d84732ee8d62ee980b',receipt['binary_sha256']).replace('recover_cli.py、binary-recovery.json、plan.json保存來源、包完整性、版本、雙方指紋及使用者選擇。','recover_cli.py、binary-recovery.json、plan.json保存本機來源、整個執行檔目錄指紋、版本、成功的啟動檢查及使用者選擇。');p.write_text(s,encoding='utf-8')
for p in root.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
print(json.dumps({'new_root':str(root),'version':receipt['version'],'binary_sha256':receipt['binary_sha256'],'old_startup_records_preserved':True}))
