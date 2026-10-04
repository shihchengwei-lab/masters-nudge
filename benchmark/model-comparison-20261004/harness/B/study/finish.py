"""Semantic execution review, frozen anonymous taste judges, and final report."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode=True
import run
import review
import blind

ROOT=run.ROOT
EXECUTION_MODEL='gpt-6-astra'
SCHEMA={'type':'object','properties':{
    'status':{'type':'string','enum':['pass','fail','environment_error']},
    'reason':{'type':'string'},
    'evidence':{'type':'array','items':{'type':'object','properties':{
        'rule':{'type':'string'},'event_lines':{'type':'array','items':{'type':'integer'}},
        'observation':{'type':'string'}},'required':['rule','event_lines','observation'],'additionalProperties':False}}
},'required':['status','reason','evidence'],'additionalProperties':False}

def wait_for_actors():
    if (ROOT/'execution-summary.json').exists():return
    pid=run.read(ROOT/'orchestrator.json')['pid']
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=kernel.OpenProcess(0x00100000,False,pid)
    if not handle:
        assert (ROOT/'execution-summary.json').exists(),'Actor process unavailable before summary'
        return
    run.emit({'stage':'awaiting_actor_completion','pid':pid})
    try:kernel.WaitForSingleObject(handle,0xFFFFFFFF)
    finally:kernel.CloseHandle(handle)

def usage(events):
    rows=[]
    for line in Path(events).read_text(encoding='utf-8').splitlines():
        try:rows.append(json.loads(line))
        except ValueError:pass
    return next((row.get('usage',{}) for row in reversed(rows) if row.get('type')=='turn.completed'),{})

def audit_one(cid,arm,plan):
    folder=run.artifact(cid,arm)
    if not (folder/'result.json').exists():return None
    if (folder/'score-v3.json').exists():return run.read(folder/'score-v3.json')
    review.export(cid,arm)
    inventory=run.read(folder/'execution-evidence.json')
    result=run.read(folder/'result.json')
    directory=ROOT/'execution-judges'/cid/arm
    directory.mkdir(parents=True,exist_ok=True)
    payload={
        'actor_task_prompt':(folder/'prompt.txt').read_text(encoding='utf-8'),
        'inventory':inventory,
        'known_runtime':{k:result[k] for k in ('actor_exit','actor_elapsed_seconds','execution_fault','tests_modified')},
        'time_limit_seconds':1800,
    }
    interference=folder/'environment-interference.json'
    if interference.exists():
        payload['verified_external_environment_interference']=run.read(interference)
        payload['interference_handling']='Do not attribute the independently confirmed Defender quarantine to an Actor edit. Review all other Actor actions normally. The first fixed verification uses the unchanged delivery and the original frozen test suite.'
    prompt=('你審核一次程式任務的執行契約，不評程式碼品味，也不重判功能驗收。'
        '以下提供原始任務指令、完整命令與改動索引。依原指令判斷：是否修改既有測試、提交、安裝、'
        '讀取Git歷史、使用外部網路或任務外材料、委派其他Agent，或未正常完成於固定30分鐘限制內。'
        '新增測試、正常執行已預裝的工具及指定公開檢查器是允許的。'
        'Masters Nudge及其Provider是本實驗授權的工具；hook-trust提示與Provider故障需分開記錄，'
        '不能直接當作Actor違反任務。命令文字包含網址、install、git等字詞本身不是違規，'
        '依實際執行的動作及上下文判斷。shell命令失敗後自行修正並完成也不等於契約失敗。'
        '可用 transcript 唯讀工具查看actor-events.jsonl、final.patch及相關執行記錄；'
        '不要讀Provider回饋，也不要新增未載於任務指令的要求。'
        '只在有具體紀錄時判fail；缺少判斷材料則environment_error；其餘判pass。'
        '每項依據指出原指令及actor-events.jsonl行號。用繁體中文輸出指定JSON。\n\n'
        +json.dumps(payload,ensure_ascii=False))
    output=directory/'output.json'
    if not output.exists():
        if (directory/'events.jsonl').exists():raise RuntimeError('Preserved incomplete execution judge: '+str(directory))
        (directory/'prompt.txt').write_text(prompt,encoding='utf-8')
        run.save(directory/'schema.json',SCHEMA)
        helper=run.load_harness('execution_review_helper')
        config={'command':sys.executable,'args':[str(run.PACKAGE/'masters_nudge/read_only_repo_mcp.py'),
             '--root',str(folder),'--budget','400000','--audit',str(directory/'reads.jsonl')],
             'enabled':True,'startup_timeout_sec':30,'tool_timeout_sec':60,'default_tools_approval_mode':'approve',
             'env':{'PYTHONIOENCODING':'utf-8'}}
        command=[plan['codex_binary'],'-c','project_doc_max_bytes=0','-c','features.multi_agent=false',
            '-c','model_reasoning_effort="medium"','-c','web_search="disabled"','-c','features.shell_tool=false',
            '--disable','hooks','--disable','plugins','-c','mcp_servers.transcript='+helper.toml(config),
            'exec','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--ephemeral','--json',
            '-s','read-only','-m',EXECUTION_MODEL,'-C',str(directory),'--output-schema',str(directory/'schema.json'),
            '-o',str(output),'-']
        run.save(directory/'launch.json',{'command':command,'prompt_sha256':run.textsha(prompt),
            'inventory_sha256':run.sha(folder/'execution-evidence.json')})
        env=os.environ.copy();env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',MASTERS_NUDGE_ACTIVE='0')
        started=time.monotonic()
        with (directory/'events.jsonl').open('w',encoding='utf-8') as stdout,(directory/'stderr.txt').open('w',encoding='utf-8') as stderr:
            process=subprocess.Popen(command,cwd=directory,env=env,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,
                text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
            try:process.communicate(prompt,timeout=900)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill.exe','/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=30)
                raise RuntimeError('Execution judge timeout: '+str(directory))
        run.save(directory/'transport.json',{'exit_code':process.returncode,'seconds':time.monotonic()-started,
            'usage':usage(directory/'events.jsonl')})
        if process.returncode or not output.exists():raise RuntimeError('Execution judge infrastructure failure: '+str(directory))
    judgment=run.read(output)
    decision={'status':judgment['status'],'reviewer':EXECUTION_MODEL+' medium - semantic execution-contract review',
        'reason':judgment['reason'],'patch_sha256':run.sha(folder/'final.patch'),
        'execution_evidence_sha256':run.sha(folder/'execution-evidence.json'),
        'evidence':[{'file':'actor-events.jsonl','sha256':run.sha(folder/'actor-events.jsonl'),'observations':judgment['evidence']},
                    {'file':str(output),'sha256':run.sha(output)}]}
    run.save(folder/'execution-review.json',decision)
    record=review.score(cid,arm)
    run.emit({'stage':'execution_review_complete',**record})
    return record

def summarize(plan):
    deliveries=[]
    for cid in plan['cases']:
        for arm in plan['comparison_arms']:
            folder=run.artifact(cid,arm)
            if not (folder/'result.json').exists():continue
            r=run.read(folder/'result.json');s=run.read(folder/'score-v3.json') if (folder/'score-v3.json').exists() else {}
            a=r.get('actor_usage',{});p=r.get('provider_usage',{})
            total={key:int(a.get(key,0))+int(p.get(key,0)) for key in ('input_tokens','cached_input_tokens','output_tokens')}
            total['uncached_input_tokens']=total['input_tokens']-total['cached_input_tokens']
            deliveries.append({'case':cid,'arm':arm,'completed':s.get('task_completed'),'fixed_status':s.get('status'),
                'execution_status':s.get('execution_contract_status'),'failed_checks':s.get('failed_checks',[]),
                'seconds':r['actor_elapsed_seconds'],'tokens':total,'actor_usage':a,'provider_usage':p,
                'actor_usage_available':bool(a),'provider_faults':r['provider_fault_count'],
                'provider_feedback':r['provider_feedback_count'],'fault':r['execution_fault']})
    arms={}
    for arm in ('A','B'):
        rows=[r for r in deliveries if r['arm'].startswith(arm)]
        arms[arm]={'scheduled':24,'recorded':len(rows),'completed':sum(r['completed'] is True for r in rows),
            'failed':sum(r['completed'] is False for r in rows),'unresolved':24-sum(r['completed'] is not None for r in rows),
            'seconds':sum(r['seconds'] for r in rows),'usage_missing':sum(not r['actor_usage_available'] for r in rows),
            'tokens':{key:sum(r['tokens'][key] for r in rows) for key in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')},
            'provider_faults':sum(r['provider_faults'] for r in rows),'provider_feedback':sum(r['provider_feedback'] for r in rows)}
    pairs=[]
    for cid in plan['cases']:
        for trial in (1,2):
            path=blind.ROOT/'judges'/cid/('trial-'+str(trial))/'A-B/pair.json'
            if path.exists():pairs.append(run.read(path))
    tastes=[p for p in pairs if p['status']=='blind_complete']
    taste=dict(Counter(p['winner'] for p in tastes))
    judgments=[]
    for path in (ROOT/'execution-judges').glob('*/*/transport.json'):judgments.append(run.read(path))
    for path in blind.ROOT.glob('judges/*/trial-*/A-B/judge-*/result.json'):
        x=run.read(path);judgments.append({'usage':x.get('usage',{}),'seconds':x['elapsed_seconds']})
    grading={'calls':len(judgments),'seconds':sum(x['seconds'] for x in judgments),
        'tokens':{key:sum(int(x.get('usage',{}).get(key,0)) for x in judgments) for key in ('input_tokens','cached_input_tokens','output_tokens')}}
    summary={'arms':arms,'taste_jointly_completed_pairs':len(tastes),'taste':taste,'pair_count':len(pairs),
        'deliveries':deliveries,'pairs':pairs,'grading_cost_separate':grading,'plan_sha256':run.sha(ROOT/'plan.json')}
    run.save(ROOT/'results-summary.json',summary)
    A=arms['A'];B=arms['B']
    diff=lambda key:f'{(B[key]/A[key]-1)*100:+.1f}%' if A[key] else '無法比較'
    token_diff=lambda key:f'{(B["tokens"][key]/A["tokens"][key]-1)*100:+.1f}%' if A['tokens'][key] else '無法比較'
    report=f'''# 12 題：全新 B 對比封存 A

A 沿用 2026-09-30 研究封存的直接實作結果；B 使用2026-10-01定稿的責任／資料區別／資訊版本全新實作。每題各兩次，A／B 各 24 份；只有 B 的 24 份是本次新執行。Actor／Provider 均 GPT-6.1 Sol medium，B 最多三則提醒。固定驗收與匿名品味準則沿用 evaluation-v3。

| 指標 | A 直接做 | B 加工具 |
|---|---:|---:|
| 契約完成 | {A['completed']}/24 | {B['completed']}/24 |
| 已判失敗 | {A['failed']} | {B['failed']} |
| 尚未判定或未執行 | {A['unresolved']} | {B['unresolved']} |
| Actor 總耗時（包含等待 Provider） | {A['seconds']/60:.1f} 分鐘 | {B['seconds']/60:.1f} 分鐘 |
| 未快取輸入 Token（Actor＋Provider） | {A['tokens']['uncached_input_tokens']:,} | {B['tokens']['uncached_input_tokens']:,} |
| 快取輸入 Token（Actor＋Provider） | {A['tokens']['cached_input_tokens']:,} | {B['tokens']['cached_input_tokens']:,} |
| 輸出 Token（Actor＋Provider） | {A['tokens']['output_tokens']:,} | {B['tokens']['output_tokens']:,} |

B 相對 A：耗時 {diff('seconds')}，未快取輸入 {token_diff('uncached_input_tokens')}，輸出 {token_diff('output_tokens')}。

兩臂都完成契約的 {len(tastes)} 對，匿名品味盲評：B 勝 {taste.get('B',0)}、A 勝 {taste.get('A',0)}、持平 {taste.get('tie',0)}。兩次獨立 Astra medium 評審交換 X／Y，不一致才加入第三次；原始票數保留。

B 共送出 {B['provider_feedback']} 則提醒、Provider 故障 {B['provider_faults']} 次。Actor 用量缺少紀錄：A {A['usage_missing']} 份、B {B['usage_missing']} 份。若有缺漏，表內 Token 是已記錄用量。

評分花費另外列出：{grading['calls']} 次模型評分呼叫，{grading['seconds']/60:.1f} 分鐘；輸入 {grading['tokens']['input_tokens']:,}、其中快取 {grading['tokens']['cached_input_tokens']:,}、輸出 {grading['tokens']['output_tokens']:,} Token。這些不算入工具相對直接實作的花費。此次使用 Codex 帳號，用量與時間是可核對的花費紀錄，沒有逐次金額帳單。

## 逐題契約與品味

| 題目／次數 | A 契約 | B 契約 | 共同完成後的品味 |
|---|---|---|---|
'''
    lookup={(r['case'],r['arm']):r for r in deliveries}
    pairlookup={(p['case'],p['trial']):p for p in pairs}
    label=lambda r:'完成' if r and r['completed'] is True else '失敗' if r and r['completed'] is False else '未定'
    for cid in plan['cases']:
        for trial in (1,2):
            pair=pairlookup.get((cid,trial),{})
            winner=pair.get('winner') if pair.get('status')=='blind_complete' else '—'
            report+=f"| {cid}／{trial} | {label(lookup.get((cid,'A'+str(trial))))} | {label(lookup.get((cid,'B'+str(trial))))} | {winner} |\n"
    report+='\n原始執行、修改、固定驗收、執行契約判讀、匿名評審與花費明細保存在本資料夾。完整資料見 [results-summary.json]('+str(ROOT/'results-summary.json').replace('\\','/')+')。\n'
    (ROOT/'REPORT.zh-TW.md').write_text(report,encoding='utf-8')
    run.emit({'stage':'report_written','arms':arms,'taste':taste,'jointly_completed_pairs':len(tastes),'root':str(ROOT)})

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    plan=run.prepare()
    run.save(ROOT/'grading-protocol.json',{'execution_review':'Semantic Astra medium review of actual transcript against original execution rules.',
        'execution_model':EXECUTION_MODEL,'reasoning':'medium','schema':SCHEMA,
        'taste_model':blind.MODEL,'taste_rubric_sha256':run.textsha(blind.RUBRIC),
        'taste_schema':blind.SCHEMA,'taste_rule':'Two reversed independent orders; third for disagreement; majority or tie.',
        'criteria_and_fixed_checks':'Frozen before Actors; no extra contractual demands.',
        'cost_rule':'Report grading separately from Actor plus Provider costs.'})
    wait_for_actors()
    if not (ROOT/'execution-summary.json').exists():raise RuntimeError('No final execution summary')
    actor_summary=run.read(ROOT/'execution-summary.json')
    if actor_summary['errors'] or actor_summary['completed']!=24:
        run.emit({'stage':'execution_incomplete','completed':actor_summary['completed'],'errors':actor_summary['errors']})
        return
    jobs=[(cid,arm) for cid in plan['cases'] for arm in plan['new_arms']]
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending={pool.submit(audit_one,cid,arm,plan):(cid,arm) for cid,arm in jobs}
        for future in as_completed(pending):future.result()
    blind.ROOT.mkdir(exist_ok=True)
    for cid in plan['cases']:
        for trial in (1,2):
            pair=blind.run_pair(cid,trial,'A-B',plan)
            if pair is None:raise RuntimeError('Unresolved execution contract: '+cid)
        blind.remove_sources(cid)
    run.verify_archive(plan)
    summarize(plan)

if __name__=='__main__':main()
