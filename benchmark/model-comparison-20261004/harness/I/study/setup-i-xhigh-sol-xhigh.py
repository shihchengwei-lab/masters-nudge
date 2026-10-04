"""New I24 study: Sol xhigh Actor and Sol xhigh Provider; immutable C/F."""
from pathlib import Path
import ast, re, shutil, json

BASE=Path('E:/masters-nudge-benchmark')
SRC=BASE/'sol61-f-xhigh-sol-provider-12case-20261002'
OUT=BASE/'sol61-i-xhigh-sol-xhigh-provider-12case-20261004'
assert not OUT.exists(), OUT
OUT.mkdir()

def write(name,text):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix=='.py':ast.parse(text)
    p.write_text(text,encoding='utf-8',newline='\n')

def remap(text):
    text=re.sub(r'([EF])_prompt_sha256',lambda m:{'E':'F','F':'I'}[m[1]]+'_prompt_sha256',text)
    text=text.replace('F_only_completed','I_only_completed')
    text=text.replace('sol61-xhigh-astra-provider-12case-20261002','sol61-f-xhigh-sol-provider-12case-20261002')
    text=text.replace('E_REFERENCE','F_REFERENCE').replace('references_C_E','references_C_F')
    text=text.replace('new_F_deliveries','new_I_deliveries').replace('F_execution_status','I_execution_status')
    text=text.replace("'CEF'","'CFI'").replace("'CE'","'CF'")
    return re.sub(r'\b([EF])(?!:)(?=(?:[12]|24)?\b)',lambda m:{'E':'F','F':'I'}[m[1]],text)

for name in ('frozen-plugin','frozen-evaluation','frozen-cli','prompts'):
    shutil.copytree(SRC/name,OUT/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
runtime=OUT/'frozen-plugin/masters_nudge/runtime.py'
old=runtime.read_text(encoding='utf-8')
assert old.count('PROVIDER_REASONING_EFFORT = "medium"')==1
runtime.write_text(old.replace('PROVIDER_REASONING_EFFORT = "medium"','PROVIDER_REASONING_EFFORT = "xhigh"'),encoding='utf-8',newline='\n')
for name in ('actor_runner.py','run.py','review.py','blind.py','transcript_reader.py','finish.py','pipeline.py','preflight.py','snapshot_harness.py','report.py','verify_final.py','diagnostic_clap_occurrences.py'):
    text=remap((SRC/name).read_text(encoding='utf-8'))
    if name=='actor_runner.py':
        text=text.replace("'provider_reasoning':'medium'","'provider_reasoning':'xhigh'")
    elif name=='run.py':
        text=text.replace('Sol medium Provider','Sol xhigh Provider')
        text=text.replace("'provider_reasoning':'medium'","'provider_reasoning':'xhigh'")
        text=text.replace("assert files(PACKAGE)==files(F_REFERENCE/'frozen-plugin')", "assert_package_delta()")
        text=text.replace("('gpt-6-astra' if a=='F' else None)","('gpt-6.1-sol' if a=='F' else None)")
        text=text.replace('only Provider Astra -> Sol','only Provider medium -> xhigh')
        text=text.replace('Actor plus Provider for F/I','Actor plus Provider for F/I')
        point=text.index('\ndef prepare():')
        text=text[:point]+'''
def assert_package_delta():
    before=files(F_REFERENCE/'frozen-plugin');after=files(PACKAGE)
    assert before.keys()==after.keys()
    delta=[p for p in before if before[p]!=after[p]]
    assert delta==['masters_nudge/runtime.py'], delta
    a=(F_REFERENCE/'frozen-plugin/masters_nudge/runtime.py').read_text(encoding='utf-8')
    b=(PACKAGE/'masters_nudge/runtime.py').read_text(encoding='utf-8')
    assert a.replace('PROVIDER_REASONING_EFFORT = "medium"','PROVIDER_REASONING_EFFORT = "xhigh"')==b
    return delta
''' + text[point:]
        text=text.replace("plan={**old,'name':", "plan={**old,'provider_effort_only_delta':assert_package_delta(),'name':")
    elif name=='preflight.py':
        text=text.replace('Sol medium','Sol xhigh').replace('PROVIDER_REASONING_EFFORT = "medium"','PROVIDER_REASONING_EFFORT = "xhigh"')
        text=text.replace("'provider_reasoning':'medium'","'provider_reasoning':'xhigh'")
        text=text.replace("run.verify_archive(plan)","run.verify_archive(plan)\nrun.assert_package_delta()")
    elif name=='verify_final.py':
        text=text.replace("r['provider_reasoning']=='medium'","r['provider_reasoning']=='xhigh'")
        text=text.replace("'provider_reasoning':'medium'","'provider_reasoning':'xhigh'")
        text=text.replace("summary['arms']['F']['completed']", "summary['arms']['F']['completed']")
        text=text.replace("run.verify_archive(plan)","run.verify_archive(plan)\nrun.assert_package_delta()")
    elif name=='snapshot_harness.py':
        text=text.replace("copy('E:/masters-nudge-benchmark/setup-f-xhigh-sol-20261002.py','study/setup-f-xhigh-sol.py')", "copy('E:/masters-nudge-benchmark/setup-i-xhigh-sol-xhigh-20261004.py','study/setup-i-xhigh-sol-xhigh.py')")
        text=text.replace('actor-runner-from-E.patch','actor-runner-from-F.patch')
    elif name=='report.py':
        text=text.replace("arms['F']['completed']==10", "arms['F']['completed']==11")
        text=text.replace('Sol xhigh＋Sol medium：','Sol xhigh＋Sol xhigh：')
        text=text.replace('Provider為GPT-6.1 Sol medium。主要比較C（Sol xhigh直接做）與F（Sol xhigh＋GPT-6 Astra medium）','Provider為GPT-6.1 Sol xhigh。主要比較C（Sol xhigh直接做）與F（Sol xhigh＋GPT-6.1 Sol medium）')
        text=text.replace('F xhigh＋Astra | I xhigh＋Sol','F xhigh＋Sol medium | I xhigh＋Sol xhigh')
        text=text.replace('Actor xhigh、Provider medium、任務、基底','Actor xhigh、任務、基底')
        text=text.replace('僅換Provider模型','僅將Provider深度從medium提高至xhigh')
    write(name,text)

(OUT/'diagnostics/flipt-segments').mkdir(parents=True)
(OUT/'diagnostics/clap-2297').mkdir()
for name in ('flipt-segments/rollout_legacy_shape_audit_test.go','clap-2297/diagnostic_occurrences.rs'):
    shutil.copy2(SRC/'diagnostics'/name,OUT/'diagnostics'/name)
write('diagnostics/flipt-segments/run.py',remap((SRC/'diagnostics/flipt-segments/run.py').read_text(encoding='utf-8')))
shutil.copy2(__file__,OUT/'setup.py')
print(json.dumps({'study':str(OUT),'new_arm':'I','actor':'gpt-6.1-sol xhigh','provider':'gpt-6.1-sol xhigh','new_deliveries':24}))
