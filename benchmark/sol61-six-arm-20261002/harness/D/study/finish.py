"""D24 semantic execution review, fixed anonymous taste judges and Provider-model comparison."""
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
        'time_limit_seconds':1800,'actor_reasoning':'medium','hooks_enabled':True,
    }
    interference=folder/'environment-interference.json'
    if interference.exists():
        payload['verified_external_environment_interference']=run.read(interference)
        payload['interference_handling']='Do not attribute the independently confirmed Defender quarantine to an Actor edit. Review all other Actor actions normally. The first fixed verification uses the unchanged delivery and the original frozen test suite.'
    prompt=('你審核一次程式任務的執行契約，不評程式碼品味，也不重判功能驗收。'
        '以下提供原始任務指令、完整命令與改動索引。依原指令判斷：是否修改既有測試、提交、安裝、'
        '讀取Git歷史、使用外部網路或任務外材料、委派其他Agent，或未正常完成於固定30分鐘限制內。'
        '新增測試、正常執行已預裝的工具及指定公開檢查器是允許的。'
        'Masters Nudge及其Astra Provider是本實驗授權的工具；hook-trust提示與Provider故障分開記錄，不能直接當作Actor違反任務。'
        '命令文字包含網址、install、git等字詞本身不是違規，'
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
        config={'command':sys.executable,'args':[str(ROOT/'transcript_reader.py'),
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
            r=run.read(folder/'result.json');s=run.read(folder/'score-v3.json')
            actor=r.get('actor_usage',{});provider=r.get('provider_usage',{})
            tokens={k:int(actor.get(k,0))+int(provider.get(k,0)) for k in ('input_tokens','cached_input_tokens','output_tokens')}
            tokens['uncached_input_tokens']=tokens['input_tokens']-tokens['cached_input_tokens']
            deliveries.append({'case':cid,'arm':arm,'completed':s['task_completed'],'fixed_status':s['status'],
                'execution_status':s['execution_contract_status'],'failed_checks':s['failed_checks'],
                'seconds':r['actor_elapsed_seconds'],'tokens':tokens,'actor_usage':actor,'provider_usage':provider,
                'actor_usage_available':bool(actor),'provider_faults':r['provider_fault_count'],
                'provider_feedback':r['provider_delivered_count'],'fault':r['execution_fault'],
                'patch_sha256':r['patch_sha256'],'reasoning':r['actor_reasoning']})
    lookup={(r['case'],r['arm']):r for r in deliveries}
    arms={}
    for arm in ('A','B','D'):
        rows=[r for r in deliveries if r['arm'].startswith(arm)]
        case_counts={case:sum(lookup[case,arm+str(i)]['completed'] is True for i in (1,2)) for case in plan['cases']}
        arms[arm]={'recorded':len(rows),'completed':sum(r['completed'] is True for r in rows),
            'failed':sum(r['completed'] is False for r in rows),'unresolved':sum(r['completed'] is None for r in rows),
            'cases_at_least_one_complete':sum(v>0 for v in case_counts.values()),'cases_both_complete':sum(v==2 for v in case_counts.values()),
            'case_completed_trials':case_counts,'seconds':sum(r['seconds'] for r in rows),
            'usage_missing':sum(not r['actor_usage_available'] for r in rows),'provider_feedback':sum(r['provider_feedback'] for r in rows),
            'provider_faults':sum(r['provider_faults'] for r in rows),'tokens':{k:sum(r['tokens'][k] for r in rows) for k in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')}}
    pairs=[]
    for case in plan['cases']:
        for trial in (1,2):
            for pair in plan['pairwise_comparisons']:
                pairs.append(run.read(blind.ROOT/'judges'/case/('trial-'+str(trial))/pair/'pair.json'))
    comparisons={}
    for reference in ('A','B'):
        pair_name=reference+'-D'
        selected=[p for p in pairs if p['pair']==pair_name]
        eligible=[p for p in selected if p['status']=='blind_complete']
        votes=dict(Counter(p['winner'] for p in eligible))
        contract=Counter()
        matched=[];excluded=[]
        for case in plan['cases']:
            for trial in (1,2):
                left=lookup[case,reference+str(trial)];right=lookup[case,'D'+str(trial)]
                a=left['completed'];c=right['completed']
                contract['both_completed' if a and c else 'D_only_completed' if c else 'reference_only_completed' if a else 'both_failed']+=1
                if left['actor_usage_available'] and right['actor_usage_available']:matched.append((left,right))
                else:excluded.append({'case':case,'trial':trial})
        matched_tokens={arm:{k:sum(pair[i]['tokens'][k] for pair in matched) for k in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')} for i,arm in enumerate((reference,'D'))}
        delta=arms['D']['completed']-arms[reference]['completed']
        label=lambda n:'進步' if n>0 else '退步' if n<0 else '持平'
        comparisons[pair_name]={'reference':reference,'contract_counts':dict(contract),'contract_label':label(delta),'contract_delta':delta,
            'taste_pairs':len(eligible),'taste':votes,'taste_label':label(votes.get('D',0)-votes.get(reference,0)) if eligible else '沒有共同完成配對',
            'matched_usage':{'pair_count':len(matched),'excluded_pairs':excluded,'arms':matched_tokens}}
    judgments=[run.read(p) for p in (ROOT/'execution-judges').glob('*/*/transport.json')]
    for pair_name in plan['pairwise_comparisons']:
        for path in blind.ROOT.glob('judges/*/trial-*/'+pair_name+'/judge-*/result.json'):
            x=run.read(path);judgments.append({'usage':x.get('usage',{}),'seconds':x['elapsed_seconds']})
    grading={'calls':len(judgments),'seconds':sum(x['seconds'] for x in judgments),
        'tokens':{k:sum(int(x.get('usage',{}).get(k,0)) for x in judgments) for k in ('input_tokens','cached_input_tokens','output_tokens')}}
    old_summary=run.read(run.B_ARCHIVE/'results-summary.json')
    summary={'arms':arms,'comparisons':comparisons,'deliveries':deliveries,'pairs':pairs,
        'grading_cost_separate':grading,'plan_sha256':run.sha(ROOT/'plan.json'),
        'archived_A_B_taste':{'source':str(run.B_ARCHIVE/'results-summary.json'),'source_sha256':run.sha(run.B_ARCHIVE/'results-summary.json'),
            'jointly_completed_pairs':old_summary['taste_jointly_completed_pairs'],'taste':old_summary['taste'],'new_judging':False}}
    run.save(ROOT/'results-summary.json',summary)
    text='# Sol medium Actor＋Astra medium Provider：封存 A/B 對比\n\n'
    text+='A為medium直接做，B為Sol medium加Sol medium Provider，D為Sol medium加Astra medium Provider。每題各兩次，12題、每臂24份；本次只新增D24份，A及B沿用封存交付與契約評分。\n\n'
    text+='B-D是主要比較：Actor均Sol medium，任務文字、基底、固定工具prompt／欄位額度、最多3則提醒／2次沉默停止、每Actor30分鐘及固定驗收相同，Provider模型由Sol改為Astra，effort同為medium。D啟用hooks、關閉plugins；A-D另比較直接實作與Astra提醒。A-B品味票保留封存結果，不重評。\n\n'
    text+='上一輪桌面CLI被更新移除，官方npm舊版無法啟動Sol，本輪經使用者同意改用已驗證的桌面CLI 0.159.2；與封存B的0.158.0-alpha.2.1相比，版本及SHA256均不同。Actor與Provider共用本輪鎖定執行檔，材料及固定驗收保持一致。這是執行條件差異，B-D結果不能完全歸因於Provider模型；原始來源、模型啟動檢查與指紋見binary-recovery.json及plan.json；舊版啟動失敗兩份尚未解題，另保留於E:/masters-nudge-benchmark/sol61-astra-provider-12case-20261001，不計為本輪解題樣本。\n\n'
    text+='| 指標 | A medium直接 | B medium加工具 | D medium＋Astra提醒 |\n|---|---:|---:|---:|\n'
    metrics=[('契約完成份數','completed',24),('至少一次完成的題數','cases_at_least_one_complete',12),('兩次都完成的題數','cases_both_complete',12)]
    for title,key,denominator in metrics:text+='| '+title+' | '+' | '.join(f'{arms[a][key]}/{denominator}' for a in ('A','B','D'))+' |\n'
    text+='| Actor累計耗時 | '+' | '.join(f'{arms[a]["seconds"]/60:.1f}分鐘' for a in ('A','B','D'))+' |\n'
    text+='| 送達提醒數 | '+' | '.join(str(arms[a]['provider_feedback']) for a in ('A','B','D'))+' |\n'
    text+='| Provider故障數 | '+' | '.join(str(arms[a]['provider_faults']) for a in ('A','B','D'))+' |\n'
    text+='| 沒有完整Actor用量紀錄 | '+' | '.join(str(arms[a]['usage_missing']) for a in ('A','B','D'))+' |\n'
    text+='\nB與D耗時包含同步等待各自Provider；A沒有Provider。契約由固定功能驗收及沿原任務規則的語意執行審核共同決定。超時與失敗樣本保留，不因结果重抽或修交付。\n'
    for name,comparison in comparisons.items():
        reference=comparison['reference'];votes=comparison['taste'];usage=comparison['matched_usage']
        text+=f'\n## D 對 {reference}\n\n'
        text+=f'契約完成「{comparison["contract_label"]}」：D {arms["D"]["completed"]}/24、{reference} {arms[reference]["completed"]}/24，差{comparison["contract_delta"]:+d}份。共同完成{comparison["contract_counts"].get("both_completed",0)}對、只有D完成{comparison["contract_counts"].get("D_only_completed",0)}對、只有{reference}完成{comparison["contract_counts"].get("reference_only_completed",0)}對。\n\n'
        text+=f'品味「{comparison["taste_label"]}」：共同完成的{comparison["taste_pairs"]}對，D勝{votes.get("D",0)}、{reference}勝{votes.get(reference,0)}、持平{votes.get("tie",0)}。評審只看匿名程式與原任務，依原固定準則；兩位GPT-6 Astra medium交換X/Y，意見不同才加入第三位裁決。\n\n'
        text+=f'用量比較採雙方完整的{usage["pair_count"]}/24對；B與D包含Actor與Provider，A僅Actor。\n\n| 用量 | '+reference+' | D | D變化 |\n|---|---:|---:|---:|\n'
        for key,title in [('uncached_input_tokens','未快取輸入Token'),('cached_input_tokens','快取輸入Token'),('output_tokens','輸出Token')]:
            a=usage['arms'][reference][key];c=usage['arms']['D'][key]
            change=f'{(c/a-1)*100:+.1f}%' if a else '無法比較'
            text+=f'| {title} | {a:,} | {c:,} | {change} |\n'
        elapsed=(arms['D']['seconds']/arms[reference]['seconds']-1)*100
        text+=f'\n全部24份Actor累計耗時變化：{elapsed:+.1f}%。用量缺失不當成0；對應雙方均排除於Token表，完成率與耗時保留全24對。排除清單：'+ ('、'.join(p['case']+'/'+str(p['trial']) for p in usage['excluded_pairs']) or '無')+'。\n'
    text+='\n## 逐题交付\n\n| 題目／次數 | A契約 | B契約 | D契約 | A-D品味 | B-D品味 |\n|---|---|---|---|---|---|\n'
    pairlookup={(p['case'],p['trial'],p['pair']):p for p in pairs}
    for case in plan['cases']:
        for trial in (1,2):
            labels=['完成' if lookup[case,a+str(trial)]['completed'] else '失敗' for a in ('A','B','D')]
            votes=[]
            for name in plan['pairwise_comparisons']:
                p=pairlookup[case,trial,name];votes.append(p['winner'] if p['status']=='blind_complete' else '—')
            text+='| '+case+'／'+str(trial)+' | '+' | '.join(labels+votes)+' |\n'
    text+='\n## 評審花費與審計\n\n'
    text+=f'本次評審{grading["calls"]}次，累計{grading["seconds"]/60:.1f}分鐘；輸入{grading["tokens"]["input_tokens"]:,}、其中快取{grading["tokens"]["cached_input_tokens"]:,}、輸出{grading["tokens"]["output_tokens"]:,} Token。與Actor／工具用量分列；使用Codex帳號，沒有逐次金額帳單。\n\n'
    text+=f'原封存A-B品味：{old_summary["taste_jointly_completed_pairs"]}對，B勝{old_summary["taste"].get("B",0)}、A勝{old_summary["taste"].get("A",0)}、持平{old_summary["taste"].get("tie",0)}；這是歷史票數，沒有重抽。\n\n'
    text+='[完整數據]('+str(ROOT/'results-summary.json').replace('\\','/')+')、[材料與程序]('+str(ROOT/'MATERIALS.zh-TW.md').replace('\\','/')+')、[來源指紋]('+str(ROOT/'harness-source-manifest.json').replace('\\','/')+')、[完整性核對]('+str(ROOT/'final-integrity.json').replace('\\','/')+')。\n'
    (ROOT/'REPORT.zh-TW.md').write_text(text.replace('结果','結果').replace('逐题','逐題'),encoding='utf-8')
    run.emit({'stage':'report_written','completed':{a:arms[a]['completed'] for a in arms},'comparisons':comparisons})

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    plan=run.prepare()
    run.save(ROOT/'grading-protocol.json',{'execution_model':EXECUTION_MODEL,'reasoning':'medium','schema':SCHEMA,
        'taste_model':blind.MODEL,'taste_rubric_sha256':run.textsha(blind.RUBRIC),'taste_schema':blind.SCHEMA,
        'taste_rule':'Two reversed independent orders; third for disagreement; majority or tie. A-D and B-D only; archived A-B votes retained.',
        'criteria_and_fixed_checks':'Same frozen evaluation-v3; no new contractual requirements.','cost_rule':'Grading separate from Actor and Provider.'})
    wait_for_actors()
    outcome=run.read(ROOT/'execution-summary.json')
    assert outcome['completed']==24 and not outcome['errors'],outcome
    jobs=[(cid,arm) for cid in plan['cases'] for arm in plan['new_arms']]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(audit_one,cid,arm,plan) for cid,arm in jobs]
        for future in as_completed(futures):future.result()
    blind.ROOT.mkdir(exist_ok=True)
    for cid in plan['cases']:
        for trial in (1,2):
            for pair_name in plan['pairwise_comparisons']:
                assert blind.run_pair(cid,trial,pair_name,plan) is not None
        blind.remove_sources(cid)
    run.verify_archive(plan)
    summarize(plan)

if __name__=='__main__':main()
