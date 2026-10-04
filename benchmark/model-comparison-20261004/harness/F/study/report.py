"""Fresh F24 versus immutable C/E with symmetrical original-clause coverage."""
from collections import Counter
import run
ROOT=run.ROOT
label=lambda v:'進步' if v>0 else '退步' if v<0 else '持平'

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
 for a in 'CEF':
  rows=[r for r in deliveries if r['arm'].startswith(a)]
  counts={cid:sum(lookup[cid,a+str(i)]['completed'] is True for i in (1,2)) for cid in plan['cases']}
  arms[a]={'recorded':24,'completed':sum(r['completed'] is True for r in rows),'frozen_completed':sum(r['frozen_completed'] is True for r in rows),
   'failed':sum(r['completed'] is False for r in rows),'unresolved':sum(r['completed'] is None for r in rows),'case_completed_trials':counts,
   'cases_at_least_one_complete':sum(v>0 for v in counts.values()),'cases_both_complete':sum(v==2 for v in counts.values()),
   'seconds':sum(r['seconds'] for r in rows),'usage_missing':sum(not r['actor_usage_available'] for r in rows),
   'provider_feedback':sum(r['provider_feedback'] for r in rows),'provider_faults':sum(r['provider_faults'] for r in rows),
   'tokens':{k:sum(r['tokens'][k] for r in rows) for k in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')}}
 assert arms['C']['completed']==13 and arms['E']['completed']==10
 pairs=[run.read(blind.ROOT/'judges'/cid/('trial-'+str(i))/pair/'pair.json') for cid in plan['cases'] for i in (1,2) for pair in plan['pairwise_comparisons']]
 comparisons={}
 for a in 'CE':
  name=a+'-F';eligible=[p for p in pairs if p['pair']==name and p['status']=='blind_complete'];votes=dict(Counter(p['winner'] for p in eligible));contract=Counter();matched=[];excluded=[]
  for cid in plan['cases']:
   for i in (1,2):
    reference=lookup[cid,a+str(i)];f=lookup[cid,'F'+str(i)]
    contract['both_completed' if reference['completed'] and f['completed'] else 'F_only_completed' if f['completed'] else 'reference_only_completed' if reference['completed'] else 'both_failed']+=1
    if reference['actor_usage_available'] and f['actor_usage_available']:matched.append((reference,f))
    else:excluded.append({'case':cid,'trial':i})
  usage={'pair_count':len(matched),'excluded_pairs':excluded,'arms':{b:{k:sum(p[n]['tokens'][k] for p in matched) for k in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')} for n,b in enumerate((a,'F'))}}
  delta=arms['F']['completed']-arms[a]['completed']
  comparisons[name]={'reference':a,'contract_counts':dict(contract),'contract_delta':delta,'contract_label':label(delta),
   'taste_pairs':len(eligible),'taste':votes,'taste_label':label(votes.get('F',0)-votes.get(a,0)) if eligible else '沒有共同完成配對','matched_usage':usage}
 judgments=[run.read(p) for p in (ROOT/'execution-judges').glob('*/*/transport.json')]
 judgments += [{'usage':r.get('usage',{}),'seconds':r['elapsed_seconds']} for p in blind.ROOT.glob('judges/*/trial-*/*/judge-*/result.json') for r in [run.read(p)]]
 grading={'calls':len(judgments),'seconds':sum(r['seconds'] for r in judgments),'tokens':{k:sum(int(r.get('usage',{}).get(k,0)) for r in judgments) for k in ('input_tokens','cached_input_tokens','output_tokens')}}
 concerns=[c for p in pairs for j in p.get('judges',[]) for c in j.get('mapped_concerns',[])]
 run.save(ROOT/'blind-contract-concerns.json',concerns)
 summary={'arms':arms,'comparisons':comparisons,'deliveries':deliveries,'pairs':pairs,'grading_cost_separate':grading,
  'plan_sha256':run.sha(ROOT/'plan.json'),'contract_coverage':'Same fixed evaluator, execution rules, and original Flipt/Clap clauses before taste.'}
 run.save(ROOT/'results-summary.json',summary)
 text='# Sol xhigh＋Sol medium：12題各兩次\n\n'
 text+='本輪只新增F24份，Actor為GPT-6.1 Sol xhigh，Provider為GPT-6.1 Sol medium。主要比較C（Sol xhigh直接做）與E（Sol xhigh＋GPT-6 Astra medium）；兩組原交付、分數与歷史評審票保留。\n\n'
 text+=f'**F對C：契約{comparisons["C-F"]["contract_label"]}、品味{comparisons["C-F"]["taste_label"]}；F對E：契約{comparisons["E-F"]["contract_label"]}、品味{comparisons["E-F"]["taste_label"]}。**\n\n'
 text+='| 指標 | C xhigh直接做 | E xhigh＋Astra | F xhigh＋Sol |\n|---|---:|---:|---:|\n'
 for title,key,den in [('契約完成（同原條款補查）','completed',24),('至少一次完成的題數','cases_at_least_one_complete',12),('兩次都完成的題數','cases_both_complete',12),('原凍結驗收完成份數','frozen_completed',24)]:
  text+='| '+title+' | '+' | '.join(str(arms[a][key])+'/'+str(den) for a in 'CEF')+' |\n'
 text+='| Actor累計分鐘 | '+' | '.join(f'{arms[a]["seconds"]/60:.1f}' for a in 'CEF')+' |\n'
 text+='| 每完成一份的分鐘（含失敗成本） | '+' | '.join(f'{arms[a]["seconds"]/60/arms[a]["completed"]:.1f}' if arms[a]['completed'] else '無完成' for a in 'CEF')+' |\n'
 for title,key in [('送達提醒數','provider_feedback'),('Provider故障數','provider_faults'),('Actor用量缺失份數','usage_missing')]:text+='| '+title+' | '+' | '.join(str(arms[a][key]) for a in 'CEF')+' |\n'
 text+='\n## 配對品味與花費\n\n'
 for a in 'CE':
  comp=comparisons[a+'-F'];v=comp['taste'];u=comp['matched_usage']
  text+=f'### F對{a}\n\n契約{comp["contract_label"]}，淨增{comp["contract_delta"]:+d}份：新增F完成{comp["contract_counts"].get("F_only_completed",0)}份，失去原完成{comp["contract_counts"].get("reference_only_completed",0)}份。共同完成{comp["taste_pairs"]}對，匿名品味F勝{v.get("F",0)}、{a}勝{v.get(a,0)}、持平{v.get("tie",0)}，判為{comp["taste_label"]}。\n\n'
  text+=f'全部24份Actor時間變化{(arms["F"]["seconds"]/arms[a]["seconds"]-1)*100:+.1f}%。Token採雙方用量完整的{u["pair_count"]}/24對；缺失不當0，完成率與耗時仍包含全部24份。\n\n| 用量 | '+a+' | F | F變化 |\n|---|---:|---:|---:|\n'
  for k,title in [('uncached_input_tokens','未快取輸入Token'),('cached_input_tokens','快取輸入Token'),('output_tokens','輸出Token')]:
   x=u['arms'][a][k];y=u['arms']['F'][k];change=f'{(y/x-1)*100:+.1f}%' if x else '無法比較'
   text+=f'| {title} | {x:,} | {y:,} | {change} |\n'
  text+='\n排除配對：'+('、'.join(r['case']+'/'+str(r['trial']) for r in u['excluded_pairs']) or '無')+'。\n\n'
 text+='## 逐題完整交付\n\n| 題目 | C | E | F | F對C | F對E |\n|---|---:|---:|---:|---|---|\n'
 for cid in plan['cases']:
  c,e,f=[arms[a]['case_completed_trials'][cid] for a in 'CEF']
  text+=f'| {cid} | {c}/2 | {e}/2 | {f}/2 | {label(f-c)} | {label(f-e)} |\n'
 text+='\n## 執行條件與審計\n\nF與E使用同一凍結桌面CLI 0.159.2及SHA 34549ded6e2aee87c911c62d025e52e26c488683d0f489cd68f756baef1a6df6；Actor xhigh、Provider medium、任務、基底、凍結工具／定稿prompt、兩工作槽、每Actor30分鐘、最多3則提醒與2次沉默停止均相同，僅換Provider模型。C使用較早CLI 0.159.0／SHA86e8ef1013f98df51fdeea446597f7e3ca32e454d1d4d8c0402a68b03c311d70；F-C是配置效益比較，包含此執行檔差異。\n\n'
 text+='三臂Flipt與Clap的六份交付使用相同原條款fixture，Clap另有原基底正向對照。原score-v3不修改，摘要另保留frozen_completed及已確認缺口；盲評僅比較共同完整交付。兩位Astra medium交换X/Y順序，意見不同才第三位，使用相同凍結準則。未復現的靜態契約疑點另列，不自動扣分。失敗與超時保留，不重抽、不修Actor交付。\n\n'
 text+=f'評審{grading["calls"]}次、累計{grading["seconds"]/60:.1f}分鐘，輸入{grading["tokens"]["input_tokens"]:,}（快取{grading["tokens"]["cached_input_tokens"]:,}）、輸出{grading["tokens"]["output_tokens"]:,}Token。評審與原生補查花費另列；Actor時間含等待Provider，Token含Actor＋Provider（C僅Actor）。沒有逐次金額帳單，不將Token當成實際金額。\n\n'
 links=[('完整數據','results-summary.json'),('材料與harness程序','MATERIALS.zh-TW.md'),('來源指紋','harness-source-manifest.json'),('原資料指紋','reference-manifest.json'),('完整性核對','final-integrity.json'),('原條款補查','diagnostics-status.json'),('盲評疑點','blind-contract-concerns.json')]
 text+='、'.join('['+title+']('+str(ROOT/path).replace('\\','/')+')' for title,path in links)+'。\n'
 (ROOT/'REPORT.zh-TW.md').write_text(text.replace('与','與').replace('交换','交換'),encoding='utf-8')
 run.emit({'stage':'report_written','completed':{a:arms[a]['completed'] for a in arms},'comparisons':comparisons})
