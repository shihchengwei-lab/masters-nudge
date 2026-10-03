"""Publish symmetric original-clause audit overlay without changing frozen scores or votes."""
from pathlib import Path
from collections import Counter
import json,hashlib,copy,shutil,subprocess,sys
import run
ROOT=run.ROOT
core=run.read(ROOT/'results-summary.json')
unchanged_paths=list((ROOT/'runs').glob('*/*/score-v3.json'))+list((ROOT/'blind-v3/judges').glob('*/*/*/judge-*/output.json'))
unchanged_hashes={str(p.relative_to(ROOT)):run.sha(p) for p in unchanged_paths}
assert run.read(ROOT/'pipeline-status.json')['status']=='complete'
proof=run.read(ROOT/'diagnostics/rollout-shape/comparison.json')
assert len(proof['rows'])==6
for row in proof['rows']:
 assert next(x for x in row['probes'] if x['case']=='scalar_key_control')['passed']
 assert row['patch_sha256']==run.sha(run.artifact('flipt-segments',row['arm'])/'final.patch')
failed=[x['arm'] for x in proof['rows'] if not next(p for p in x['probes'] if p['case']=='single_list_key')['passed']]
assert failed==['D1']
clap=run.read(ROOT/'diagnostics/clap-occurrences-valid/comparison.json')
assert len(clap['rows'])==7 and clap['baseline_occurrences']=={'non_overriding_control':2,'self_override_single_value':2,'self_override_multi_values':2}
for row in clap['rows']:
 assert row['exit_code']==0 and row['fixture_sha256']==run.sha(ROOT/'diagnostics/clap-occurrences-valid/diagnostic_occurrences.rs')
 assert next(p for p in row['probes'] if p['case']=='non_overriding_control')['occurrences']==2
 if row['arm']!='BASE':assert row['patch_sha256']==run.sha(run.artifact('clap-2297',row['arm'])/'final.patch')
assert [r['arm'] for r in clap['rows'] if not r['occurrences_preserved']]==['B1']
gaps={('flipt-segments','D1'):'Original C03: singleton list rollout export must retain key/value legacy shape.',('clap-2297','B1'):'Original occurrences clause: self-overriding options must preserve existing occurrences count; baseline 2, B1 1.'}
for filename,target in [('results-summary.json','FROZEN-EVALUATION-SUMMARY.json'),('REPORT.zh-TW.md','FROZEN-EVALUATION-REPORT.zh-TW.md'),('final-integrity.json','FROZEN-EVALUATION-INTEGRITY.json')]:
 assert not (ROOT/target).exists();shutil.copy2(ROOT/filename,ROOT/target)
rows=copy.deepcopy(core['deliveries'])
for row in rows:
 row['frozen_completed']=row['completed']
 if (row['case'],row['arm']) in gaps:
  assert row['completed'];row['completed']=False;row['confirmed_task_gap']=gaps[row['case'],row['arm']]
lookup={(r['case'],r['arm']):r for r in rows}
arms=copy.deepcopy(core['arms'])
for arm in ('A','B','D'):
 selected=[r for r in rows if r['arm'].startswith(arm)]
 counts={case:sum(lookup[case,arm+str(i)]['completed'] is True for i in (1,2)) for case in run.prepare()['cases']}
 arms[arm].update(completed=sum(r['completed'] is True for r in selected),failed=sum(r['completed'] is False for r in selected),case_completed_trials=counts,cases_at_least_one_complete=sum(v>0 for v in counts.values()),cases_both_complete=sum(v==2 for v in counts.values()))
comparisons={}
label=lambda n:'進步' if n>0 else '退步' if n<0 else '持平'
for reference in ('A','B'):
 name=reference+'-D';selected=[p for p in core['pairs'] if p['pair']==name]
 eligible=[p for p in selected if p['status']=='blind_complete' and lookup[p['case'],reference+str(p['trial'])]['completed'] and lookup[p['case'],'D'+str(p['trial'])]['completed']]
 excluded=[p for p in selected if p['status']=='blind_complete' and p not in eligible]
 contract=Counter()
 for case in run.prepare()['cases']:
  for trial in (1,2):
   a=lookup[case,reference+str(trial)]['completed'];d=lookup[case,'D'+str(trial)]['completed']
   contract['both_completed' if a and d else 'D_only_completed' if d else 'reference_only_completed' if a else 'both_failed']+=1
 votes=dict(Counter(p['winner'] for p in eligible));delta=arms['D']['completed']-arms[reference]['completed']
 comparisons[name]={**core['comparisons'][name],'contract_counts':dict(contract),'contract_delta':delta,'contract_label':label(delta),'taste_pairs':len(eligible),'taste':votes,'taste_label':label(votes.get('D',0)-votes.get(reference,0)),'eligible_pairs':eligible,'excluded_recorded_taste_pairs':excluded}
assert arms['A']['completed']==6 and arms['B']['completed']==8 and arms['D']['completed']==8
assert comparisons['A-D']['taste_pairs']==5 and comparisons['B-D']['taste_pairs']==5
assert comparisons['B-D']['taste']=={'tie':2,'D':1,'B':2}
concerns=[]
for path in sorted((ROOT/'blind-v3/judges').glob('*/*/*/judge-*/output.json')):
 output=run.read(path);launch=run.read(path.parent/'launch.json')
 for concern in output['contract_concerns']:
  arm=launch['mapping'][concern['candidate']];case=path.parent.parent.parent.parent.name
  confirmed=(case=='flipt-segments' and arm=='D1' and 'exporter.go' in concern['location']) or (case=='clap-2297' and arm=='B1' and 'occurrences' in concern['exact_clause'])
  concerns.append({'case':case,'arm':arm,'exact_clause':concern['exact_clause'],'location':concern['location'],'observation':concern['observation'],'source':str(path),'status':'confirmed_by_symmetric_original_clause_probe' if confirmed else 'unconfirmed_static_concern_not_counted_as_failure'})
run.save(ROOT/'blind-contract-concerns.json',concerns)
proof_hashes={name:run.sha(ROOT/path) for name,path in [('flipt','diagnostics/rollout-shape/comparison.json'),('clap','diagnostics/clap-occurrences-valid/comparison.json')]}
updated={'scope':'Same frozen evaluator plus two original-clause diagnostics applied symmetrically to all six relevant A/B/D deliveries; Clap also probes baseline. Archived scores are not replaced or rescored.','source_frozen_summary_sha256':run.sha(ROOT/'FROZEN-EVALUATION-SUMMARY.json'),'diagnostic_proof_sha256':proof_hashes,'confirmed_task_gaps':[{'case':case,'arm':arm,'clause':clause} for (case,arm),clause in gaps.items()],'arms':arms,'comparisons':comparisons,'deliveries':rows,'grading_cost_separate':core['grading_cost_separate'],'unconfirmed_blind_concerns':[c for c in concerns if c['status'].startswith('unconfirmed')],'unchanged_tokens_and_time':True,'no_new_actors_or_judges':True}
run.save(ROOT/'diagnostic-adjusted-summary.json',updated)
text='# Sol medium＋Astra medium：12題各兩次對照結果\n\n'
text+='D為Sol medium Actor＋Astra medium Provider；B為封存Sol medium Actor＋Sol medium Provider；A為封存Sol medium直接實作。這輪只新增D的24份，A/B交付、既有分數、Actor與評審票都保留。\n\n'
text+='**契約持平、程式碼品味退步、Actor累計耗時減少7.7%。** 原凍結驗收B/D均9/24；匿名評審指出原條款漏驗後，對三臂的Flipt與Clap各六份交付做同一補查，確認Flipt D1與Clap B1各漏一項原要求。加入這兩個已確認缺口後，B/D均完成8/24。本報告以此口徑作結論，原分數與原報告另封存，沒有改寫。\n\n'
text+='| 指標 | A 直接實作 | B Sol提醒 | D Astra提醒 | D對B |\n|---|---:|---:|---:|---|\n'
for title,key,den in [('契約完成份數（原驗收＋同一補查）','completed',24),('至少一次完成的題數','cases_at_least_one_complete',12),('兩次都完成的題數','cases_both_complete',12)]:
 text+='| '+title+' | '+' | '.join(f'{arms[a][key]}/{den}' for a in ('A','B','D'))+' | '+label(arms['D'][key]-arms['B'][key])+' |\n'
text+='| 原凍結驗收完成份數 | 6/24 | 9/24 | 9/24 | 持平 |\n'
text+='| Actor累計耗時 | '+' | '.join(f'{arms[a]["seconds"]/60:.1f}分鐘' for a in ('A','B','D'))+' | '+f'{(arms["D"]["seconds"]/arms["B"]["seconds"]-1)*100:+.1f}% |\n'
text+='| 送達提醒数 | '+' | '.join(str(arms[a]['provider_feedback']) for a in ('A','B','D'))+' | — |\n'
text+='| Provider故障数 | '+' | '.join(str(arms[a]['provider_faults']) for a in ('A','B','D'))+' | — |\n'
text+='\n24份D均遵守原執行規則。時間包含Actor等待Provider；Token表包含B/D的Actor＋Provider、A僅Actor。凍結功能驗收、執行规则與已確認原條款補查共同形成上表；其餘未實測的盲評疑點只列診斷，不自動扣分。\n'
for name,comparison in comparisons.items():
 ref=comparison['reference'];votes=comparison['taste'];usage=comparison['matched_usage']
 text+=f'\n## D對{ref}\n\n契約「{comparison["contract_label"]}」：D {arms["D"]["completed"]}/24、{ref} {arms[ref]["completed"]}/24。共同完成{comparison["contract_counts"].get("both_completed",0)}對，只有D完成{comparison["contract_counts"].get("D_only_completed",0)}對，只有{ref}完成{comparison["contract_counts"].get("reference_only_completed",0)}對。\n\n'
 excluded_names='、'.join(p['case']+'/'+str(p['trial']) for p in comparison['excluded_recorded_taste_pairs'])
 text+=f'品味「{comparison["taste_label"]}」：共同完成的{comparison["taste_pairs"]}對，D勝{votes.get("D",0)}、{ref}勝{votes.get(ref,0)}、持平{votes.get("tie",0)}。原凍結口徑的比較票全部保留；{excluded_names}因其中一方確認違反原契約，從此品味口徑排除，不重新投票。兩位Astra medium交換匿名X/Y，意見不同才加入第三位。\n\n'
 text+=f'用量採雙方完整的{usage["pair_count"]}/24對。\n\n| 用量 | {ref} | D | D變化 |\n|---|---:|---:|---:|\n'
 for key,title in [('uncached_input_tokens','未快取輸入Token'),('cached_input_tokens','快取輸入Token'),('output_tokens','輸出Token')]:
  a=usage['arms'][ref][key];d=usage['arms']['D'][key];change=f'{(d/a-1)*100:+.1f}%' if a else '無法比較'
  text+=f'| {title} | {a:,} | {d:,} | {change} |\n'
 text+='\n用量缺失不當0，對應雙方排除Token比較；完成率與耗時仍計全部24份。排除清單：'+('、'.join(p['case']+'/'+str(p['trial']) for p in usage['excluded_pairs']) or '無')+'。\n'
text+='\n## 逐題交付\n\n| 題目 | A完成 | B完成 | D完成 | D對B |\n|---|---:|---:|---:|---|\n'
for case in run.prepare()['cases']:
 text+='| '+case+' | '+' | '.join(str(arms[a]['case_completed_trials'][case])+'/2' for a in ('A','B','D'))+' | '+label(arms['D']['case_completed_trials'][case]-arms['B']['case_completed_trials'][case])+' |\n'
text+='\nD新增Proton不可信金鑰一份，Clap在本補查口徑由B的零份增加為兩份；NodeBB與Ansible各少一份。Flipt原驗收兩份通過，補查後D1不完整，因此本口徑為一份。至少一次完成的題數相同（5對5），兩次均完成的題數也相同（3對3），完成的題目不同。Proton不可信金鑰和Flipt兩份D都沒有收到提醒。這些是觀察到的差異，未把沒有提醒當成差異原因。\n'
text+='\n## 共同完成交付的品味比較\n\n| 題目／第幾次 | D對B | 評審觀察 |\n|---|---|---|\n| Element／1、2 | 持平、持平 | 兩臂相近，沒有足以決定勝負的結構改善。 |\n| Flipt／2 | 進步 | D先算出有效運算方式，供儲存與回傳共用；B直接改動傳入資料。D也把格式辨識集中在相關欄位。該份D沒有收到提醒。 |\n| Proton mailbox retry／1、2 | 退步、退步 | B較清楚地分開仍欠資料、請求進行中與等待期限，並共用資料需求判斷；D讓同一旗標兼任請求與等待，仍依賴跨流程交接。 |\n\n這是最終程式碼的匿名語意評分，並非提醒內容品質或採納率。品味原始位置、五條準則依據及交換順序票數可在blind-v3/judges查核；總評由共同完成的配對勝負決定。D對A的五對均勝出，對B則一勝、兩敗、兩持平。\n'
text+='\n## 已確認的漏驗與其他盲評疑點\n\n原契約C03明訂rollout沿用segment的key/value形狀。正常scalar key正向控制六份全通過；使用已有RPC的單元素SegmentKeys、OR operator時，A1/A2/B1/B2/D2仍輸出key/value，只有D1輸出keys清單。這是同一原條款的覆蓋補查，不新增任務要求；六份production patch在原映像、原基底及禁止網路的容器檢查，完整Actor與原分數均保留。\n\n'
text+='Clap原契約要求保留occurrences。原始程式與六份交付使用相同重複參數輸入；非覆寫正向控制全部維持2次。自我覆寫時，只有B1把單值及多值兩種情況的計數改成1，D1/D2保留2，且正確替換為最後一組值。A1/A2/B2保留計數但未完成覆寫要求，因此原失敗判定不變。補查使用相同凍結Cargo.lock、離線且locked的原生Cargo環境。\n\n'
text+='補查結果：[Flipt]('+str(ROOT/'diagnostics/rollout-shape/comparison.json').replace('\\','/')+')、[Clap]('+str(ROOT/'diagnostics/clap-occurrences-valid/comparison.json').replace('\\','/')+')；各份測試log、fixture、實際重現程式與指紋均保留。有效補查耗時'+f'{(sum(r["seconds"] for r in proof["rows"])+sum(r["seconds"] for r in clap["rows"]))/60:.1f}分鐘'+'，不重跑Actor或模型，與主要Actor／Provider花費分開。第一份Clap診斷fixture被原始程式拒絕，記為無效控制，修正參數設定後才採用上述結果；無效來源與log保留於diagnostics/clap-occurrences，不作契約比較。\n\n'
unknown=updated['unconfirmed_blind_concerns'];groups=Counter((c['case'],c['arm']) for c in unknown)
if groups:
 text+='其餘靜態疑點涉及'+ '、'.join(case+'/'+arm+'（'+str(count)+'筆評審記錄）' for (case,arm),count in groups.items())+'。這些尚未復現，不列為已確認失敗；逐筆原條款、位置、觀察及原始評審連結見[blind-contract-concerns.json]('+str(ROOT/'blind-contract-concerns.json').replace('\\','/')+')。\n'
text+='\n## 執行條件、成本與審計\n\n兩個工作槽、每Actor30分鐘、每題D1/D2獨立執行、最多3則提醒及2次沉默停止；原任務、基底、8映像、最終工具prompt和凍結驗收保持一致。原桌面CLI已被更新移除；官方npm同版本無法啟動Sol後，使用者同意改用已驗證的桌面0.159.2，與封存B的0.158.0-alpha.2.1版本及SHA256不同。結果包含執行環境差異，不能完全歸因Provider模型。private CLI與助手已鎖定，沒有變更全域設定。\n\n'
g=core['grading_cost_separate'];text+=f'本輪評審{g["calls"]}次，累計{g["seconds"]/60:.1f}分鐘；輸入{g["tokens"]["input_tokens"]:,}（含快取{g["tokens"]["cached_input_tokens"]:,}）、輸出{g["tokens"]["output_tokens"]:,}Token。評審另列，不計入Actor／Provider比較。使用Codex帳號，無逐次金額帳單；Token及時間不等同不同模型的實際金額。\n\n'
text+='官方npm舊版兩次啟動失敗尚未解題，保留於原D資料夾STARTUP-FAILURE.json，不列為解題樣本。桌面版Element一次服務端容量中斷45.969秒，零改檔／零Provider／無完整用量；原始紀錄另保留，確認服務恢復後只接續中斷及未執行份數，四份已完成交付原樣保留，沒有因功能失败而重抽。\n\n'
text+='原A-B品味票保留，不重評。原凍結口徑：[原報告]('+str(ROOT/'FROZEN-EVALUATION-REPORT.zh-TW.md').replace('\\','/')+')、[原摘要]('+str(ROOT/'FROZEN-EVALUATION-SUMMARY.json').replace('\\','/')+')。\n\n'
for title,path in [('包含已確認缺口的摘要','diagnostic-adjusted-summary.json'),('材料與完整harness程序','MATERIALS.zh-TW.md'),('來源指紋','harness-source-manifest.json'),('完整性核對','final-integrity.json'),('補查完整性','diagnostic-integrity.json')]:text+='['+title+']('+str(ROOT/path).replace('\\','/')+')、'
text=text.rstrip('、')+'。\n'
for wrong,right in [('规则','規則'),('意见','意見'),('失败','失敗'),('数','數')]:text=text.replace(wrong,right)
(ROOT/'REPORT.zh-TW.md').write_text(text,encoding='utf-8')
# Make the postprocessing method inspectable in addition to the untouched source snapshots.
manifest=run.read(ROOT/'harness-source-manifest.json');source=Path(__file__).resolve();snapshot=ROOT/'harness-sources/study'/source.name;shutil.copy2(source,snapshot)
manifest.append({'source':str(source),'snapshot':snapshot.relative_to(ROOT).as_posix(),'sha256':run.sha(source)});run.save(ROOT/'harness-source-manifest.json',manifest)
p=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'verify_final.py')],cwd=ROOT);assert p.returncode==0
run.verify_archive(run.prepare())
assert run.sha(ROOT/'results-summary.json')==run.sha(ROOT/'FROZEN-EVALUATION-SUMMARY.json')
assert all(run.sha(ROOT/name)==sha for name,sha in unchanged_hashes.items())
run.save(ROOT/'diagnostic-integrity.json',{'same_probe_all_six_for_both_cases':True,'Flipt_scalar_controls_pass':6,'Clap_non_overriding_controls_pass':7,'confirmed_failure':[case+'/'+arm for case,arm in gaps],'frozen_scores_and_votes_unchanged':True,'unchanged_score_and_vote_hashes':unchanged_hashes,'A_unchanged':True,'sealed_B_unchanged':True,'original_counts':{a:core['arms'][a]['completed'] for a in arms},'overlay_counts':{a:arms[a]['completed'] for a in arms},'taste_pairs_after_confirmed_gap':{k:v['taste_pairs'] for k,v in comparisons.items()},'no_new_actors_or_judges':True,'diagnostic_proof_sha256':proof_hashes,'adjusted_summary_sha256':run.sha(ROOT/'diagnostic-adjusted-summary.json'),'report_sha256':run.sha(ROOT/'REPORT.zh-TW.md'),'source_snapshot_count':len(manifest)})
print(json.dumps({'stage':'diagnostic_report_published','completed':{a:arms[a]['completed'] for a in arms},'taste':{n:c['taste'] for n,c in comparisons.items()},'source_snapshots':len(manifest)},ensure_ascii=False))
