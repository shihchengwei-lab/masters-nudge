"""Aggregate immutable D and fresh E, with symmetric original-clause coverage."""
from collections import Counter
import run
ROOT=run.ROOT
label=lambda n:'進步' if n>0 else '退步' if n<0 else '持平'

def summarize(plan):
 import blind
 deliveries=[]
 for cid in plan['cases']:
  for arm in plan['comparison_arms']:
   folder=run.artifact(cid,arm);r=run.read(folder/'result.json');s=run.completed_score(cid,arm)
   actor=r.get('actor_usage',{});provider=r.get('provider_usage',{})
   tokens={k:int(actor.get(k,0))+int(provider.get(k,0)) for k in ('input_tokens','cached_input_tokens','output_tokens')}
   tokens['uncached_input_tokens']=tokens['input_tokens']-tokens['cached_input_tokens']
   deliveries.append({'case':cid,'arm':arm,'completed':s['task_completed'],'frozen_completed':s['frozen_task_completed'],
    'confirmed_original_clause_gap':s.get('confirmed_original_clause_gap'),'fixed_status':s['status'],'execution_status':s['execution_contract_status'],
    'failed_checks':s['failed_checks'],'seconds':r['actor_elapsed_seconds'],'tokens':tokens,'actor_usage_available':bool(actor),
    'actor_usage':actor,'provider_usage':provider,'provider_faults':r['provider_fault_count'],'provider_feedback':r['provider_delivered_count'],
    'fault':r['execution_fault'],'patch_sha256':r['patch_sha256'],'reasoning':r['actor_reasoning']})
 lookup={(r['case'],r['arm']):r for r in deliveries};arms={}
 for arm in ('D','E'):
  rows=[r for r in deliveries if r['arm'].startswith(arm)]
  counts={cid:sum(lookup[cid,arm+str(i)]['completed'] is True for i in (1,2)) for cid in plan['cases']}
  arms[arm]={'recorded':24,'completed':sum(r['completed'] is True for r in rows),'frozen_completed':sum(r['frozen_completed'] is True for r in rows),
   'failed':sum(r['completed'] is False for r in rows),'unresolved':sum(r['completed'] is None for r in rows),'case_completed_trials':counts,
   'cases_at_least_one_complete':sum(v>0 for v in counts.values()),'cases_both_complete':sum(v==2 for v in counts.values()),
   'seconds':sum(r['seconds'] for r in rows),'usage_missing':sum(not r['actor_usage_available'] for r in rows),
   'provider_feedback':sum(r['provider_feedback'] for r in rows),'provider_faults':sum(r['provider_faults'] for r in rows),
   'tokens':{k:sum(r['tokens'][k] for r in rows) for k in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')}}
 assert arms['D']['completed']==8
 pairs=[run.read(blind.ROOT/'judges'/cid/('trial-'+str(i))/'D-E/pair.json') for cid in plan['cases'] for i in (1,2)]
 eligible=[p for p in pairs if p['status']=='blind_complete'];votes=dict(Counter(p['winner'] for p in eligible));contract=Counter();matched=[];excluded=[]
 for cid in plan['cases']:
  for i in (1,2):
   d=lookup[cid,'D'+str(i)];e=lookup[cid,'E'+str(i)]
   contract['both_completed' if d['completed'] and e['completed'] else 'E_only_completed' if e['completed'] else 'reference_only_completed' if d['completed'] else 'both_failed']+=1
   if d['actor_usage_available'] and e['actor_usage_available']:matched.append((d,e))
   else:excluded.append({'case':cid,'trial':i})
 usage={'pair_count':len(matched),'excluded_pairs':excluded,'arms':{a:{k:sum(p[n]['tokens'][k] for p in matched) for k in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')} for n,a in enumerate(('D','E'))}}
 comparison={'reference':'D','contract_counts':dict(contract),'contract_delta':arms['E']['completed']-arms['D']['completed'],
  'contract_label':label(arms['E']['completed']-arms['D']['completed']),'taste_pairs':len(eligible),'taste':votes,
  'taste_label':label(votes.get('E',0)-votes.get('D',0)) if eligible else '沒有共同完成配對','matched_usage':usage}
 judgments=[run.read(p) for p in (ROOT/'execution-judges').glob('*/*/transport.json')]
 judgments += [{'usage':r.get('usage',{}),'seconds':r['elapsed_seconds']} for p in blind.ROOT.glob('judges/*/trial-*/D-E/judge-*/result.json') for r in [run.read(p)]]
 grading={'calls':len(judgments),'seconds':sum(r['seconds'] for r in judgments),'tokens':{k:sum(int(r.get('usage',{}).get(k,0)) for r in judgments) for k in ('input_tokens','cached_input_tokens','output_tokens')}}
 concerns=[c for p in pairs for j in p.get('judges',[]) for c in j.get('mapped_concerns',[])]
 run.save(ROOT/'blind-contract-concerns.json',concerns)
 summary={'arms':arms,'comparisons':{'D-E':comparison},'deliveries':deliveries,'pairs':pairs,'grading_cost_separate':grading,
  'plan_sha256':run.sha(ROOT/'plan.json'),'contract_coverage':'Frozen evaluation plus the same Flipt C03 / Clap occurrences checks symmetrically applied before taste.'}
 run.save(ROOT/'results-summary.json',summary)
 text='# Sol xhigh＋Astra medium：12題各兩次\n\n'
 text+='E為Sol xhigh Actor＋Astra medium Provider；D為已完成Sol medium Actor＋Astra medium Provider。本輪只新增E24份，D交付、原分數及歷史評審票保持原樣。CLI 0.159.2及SHA、模型、工具、任務、基底、每Actor30分鐘與最多3則提醒／2次沉默停止均一致，Actor思考深度由medium改為xhigh。\n\n'
 text+=f'**契約{comparison["contract_label"]}，程式碼品味{comparison["taste_label"]}。**\n\n| 指標 | D Actor medium | E Actor xhigh | E對D |\n|---|---:|---:|---|\n'
 for title,key,den in [('契約完成（同原條款補查）','completed',24),('至少一次完成的題數','cases_at_least_one_complete',12),('兩次都完成的題數','cases_both_complete',12),('原凍結驗收完成份數','frozen_completed',24)]:
  text+=f'| {title} | {arms["D"][key]}/{den} | {arms["E"][key]}/{den} | {label(arms["E"][key]-arms["D"][key])} |\n'
 text+=f'| Actor累計耗時 | {arms["D"]["seconds"]/60:.1f}分鐘 | {arms["E"]["seconds"]/60:.1f}分鐘 | {(arms["E"]["seconds"]/arms["D"]["seconds"]-1)*100:+.1f}% |\n'
 for title,key in [('送達提醒數','provider_feedback'),('Provider故障數','provider_faults'),('Actor用量缺失份數','usage_missing')]:text+=f'| {title} | {arms["D"][key]} | {arms["E"][key]} | — |\n'
 text+=f'\n匿名品味僅比較共同完成的{len(eligible)}對：E勝{votes.get("E",0)}、D勝{votes.get("D",0)}、持平{votes.get("tie",0)}。兩位Astra medium交換X/Y順序，意見不同才加入第三位，以原凍結準則判斷。歷史D對A/B票數沒有重評。\n\n'
 text+=f'共同完成{contract["both_completed"]}對、僅E完成{contract["E_only_completed"]}對、僅D完成{contract["reference_only_completed"]}對。\n\n'
 text+='## 逐題交付\n\n| 題目 | D完成 | E完成 | E對D |\n|---|---:|---:|---|\n'
 for cid in plan['cases']:
  d=arms['D']['case_completed_trials'][cid];e=arms['E']['case_completed_trials'][cid]
  text+=f'| {cid} | {d}/2 | {e}/2 | {label(e-d)} |\n'
 text+='\n## 花費\n\n兩臂均含Actor＋Provider；Actor耗時含等待Provider。Token採雙方用量完整的'+str(len(matched))+'/24對，缺值不當0；完成率與耗時仍含全部24份。\n\n| 用量 | D | E | E變化 |\n|---|---:|---:|---:|\n'
 for key,title in [('uncached_input_tokens','未快取輸入Token'),('cached_input_tokens','快取輸入Token'),('output_tokens','輸出Token')]:
  d=usage['arms']['D'][key];e=usage['arms']['E'][key];change=f'{(e/d-1)*100:+.1f}%' if d else '無法比較'
  text+=f'| {title} | {d:,} | {e:,} | {change} |\n'
 text+='\n排除配對：'+('、'.join(r['case']+'/'+str(r['trial']) for r in excluded) or '無')+'。沒有逐次金額帳單，Token與時間不等同实际金額。\n\n'
 text+=f'評審{grading["calls"]}次、累計{grading["seconds"]/60:.1f}分鐘，輸入{grading["tokens"]["input_tokens"]:,}（快取{grading["tokens"]["cached_input_tokens"]:,}）、輸出{grading["tokens"]["output_tokens"]:,}Token；原生補查時間見diagnostics-status.json。兩者與Actor／Provider花費分開。\n\n'
 text+='## 契約覆蓋與審計\n\n原固定功能驗收及沿原任務的執行審核保持一致；另沿用D輪已確認的原條款補查，對D1/D2/E1/E2的Flipt rollout key/value格式與Clap自我覆寫occurrences做相同檢查，Clap另測原始基底。原score-v3不修改，摘要保留frozen_completed及已確認缺口。補查在盲評前完成，只對共同完整交付評品味，未確認的靜態疑點另列，不自動扣分。超時、失敗、Provider故障保留，不重抽或修Actor交付。\n\n'
 for title,path in [('完整數據','results-summary.json'),('材料與harness程序','MATERIALS.zh-TW.md'),('來源指紋','harness-source-manifest.json'),('完整性核對','final-integrity.json'),('原條款补查','diagnostics-status.json'),('盲評疑點','blind-contract-concerns.json')]:text+='['+title+']('+str(ROOT/path).replace('\\','/')+')、'
 (ROOT/'REPORT.zh-TW.md').write_text(text.rstrip('、').replace('实际','實際').replace('补查','補查')+'。\n',encoding='utf-8')
 run.emit({'stage':'report_written','completed':{a:arms[a]['completed'] for a in arms},'comparison':comparison})
