"""Add plain-language comparison and infrastructure receipts to the final report."""
from pathlib import Path
from statistics import median
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    summary_path=ROOT/'results-summary.json'
    summary=read(summary_path)
    assert all(summary['arms'][a]['recorded']==24 for a in ('A','B'))
    infra=[]
    for path in sorted((ROOT/'runs').glob('*/*/environment-interference.json')):
        value=read(path)
        folder=path.parent
        assert value['result_sha256']==sha(folder/'result.json')
        assert value['patch_sha256']==sha(folder/'final.patch')
        assert value['transcript_sha256']==sha(folder/'actor-events.jsonl')
        infra.append({'file':str(path),'sha256':sha(path),'case':value['case'],'arm':value['arm'],'classification':value['classification']})
    summary['external_environment_interference']=infra
    for a in ('A','B'):
        rows=[r for r in summary['deliveries'] if r['arm'].startswith(a)]
        summary['arms'][a]['mean_actor_seconds']=sum(r['seconds'] for r in rows)/len(rows)
        summary['arms'][a]['median_actor_seconds']=median(r['seconds'] for r in rows)
        summary['arms'][a]['fixed_verification_seconds']=sum(read(ROOT/'evaluation-v3'/r['case']/r['arm']/'evidence.json')['elapsed_seconds'] for r in rows)
    A=summary['arms']['A'];B=summary['arms']['B']
    difference=B['completed']-A['completed']
    judgment='進步' if difference>0 else '退步' if difference<0 else '持平'
    paired={'B_only_completed':0,'A_only_completed':0,'both_completed':0,'both_failed':0,'unresolved':0}
    rows={(r['case'],r['arm']):r for r in summary['deliveries']}
    usage_pairs=[]
    missing_usage_pairs=[]
    for case in sorted({r['case'] for r in summary['deliveries']}):
        for trial in (1,2):
            a=rows[(case,'A'+str(trial))]['completed'];b=rows[(case,'B'+str(trial))]['completed']
            key=('unresolved' if a is None or b is None else 'both_completed' if a and b else
                 'B_only_completed' if b else 'A_only_completed' if a else 'both_failed')
            paired[key]+=1
            ar=rows[(case,'A'+str(trial))];br=rows[(case,'B'+str(trial))]
            if ar['actor_usage_available'] and br['actor_usage_available']:
                usage_pairs.append((ar,br))
            else:
                missing_usage_pairs.append({'case':case,'trial':trial})
    summary['paired_contract_results']=paired
    summary['contract_comparison_label']=judgment
    matched={'pair_count':len(usage_pairs),'excluded_pairs':missing_usage_pairs,'arms':{}}
    for index,a in enumerate(('A','B')):
        matched['arms'][a]={k:sum(pair[index]['tokens'][k] for pair in usage_pairs) for k in ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens')}
    summary['matched_usage_comparison']=matched
    summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=ROOT/'REPORT.zh-TW.md'
    text=report.read_text(encoding='utf-8')
    ratio=lambda key:f'{(matched["arms"]["B"][key]/matched["arms"]["A"][key]-1)*100:+.1f}%' if matched['arms']['A'][key] else '無法比較'
    time_ratio=f'{(B["seconds"]/A["seconds"]-1)*100:+.1f}%' if A['seconds'] else '無法比較'
    replacement=f'B 相對 A：全 48 份耗時 {time_ratio}。Token 比率按雙方用量齊全的 {len(usage_pairs)}/24 對計算：未快取輸入 {ratio("uncached_input_tokens")}，輸出 {ratio("output_tokens")}。'
    text=re.sub(r'^B 相對 A：.*$',replacement,text,flags=re.M)
    text+=f'\n## 完成率與每份花費\n\n契約完成相對 A 為「{judgment}」：B {B["completed"]}/24、A {A["completed"]}/24，差 {difference:+d} 份。同次配對中，只有 B 完成 {paired["B_only_completed"]} 對、只有 A 完成 {paired["A_only_completed"]} 對，兩臂都完成 {paired["both_completed"]} 對。\n\n'
    text+=f'每份 Actor 平均耗時：A {A["mean_actor_seconds"]/60:.1f} 分鐘、B {B["mean_actor_seconds"]/60:.1f} 分鐘；中位數 A {A["median_actor_seconds"]/60:.1f} 分鐘、B {B["median_actor_seconds"]/60:.1f} 分鐘。Provider 等待已含在 B 的 Actor 耗時內。\n\n'
    text+=f'固定驗收另耗時：A {A["fixed_verification_seconds"]/60:.1f} 分鐘、B {B["fixed_verification_seconds"]/60:.1f} 分鐘。\n'
    if missing_usage_pairs:
        excluded='、'.join(p['case']+'／'+str(p['trial']) for p in missing_usage_pairs)
        text+=f'\nToken 比較缺少 {excluded} 的完整用量；對應同題同次的 A、B 均排除於 Token 比率，避免把缺少紀錄當成零花費。所有 48 份仍計入耗時與完成率。原表內 Token 合計為已記錄部分，用量完整配對的 A／B 合計見 results-summary.json 的 matched_usage_comparison。\n'
    if infra:
        text+='\n## 環境干擾更正\n\nNodeBB B1 的既有圖片測試素材被 Windows Defender 在 rg.exe 掃描時隔離。舊執行器誤判為 Actor 改測試，因此跳過固定驗收；原始 result 與 patch 保留。Windows 事件 1116／1117 確認隔離來源；補做第一次驗收時沿用同一凍結 Linux 測試環境、同一原始 patch，固定檢查全部通過。執行規則審查取得這項外部隔離證據，最終完成判定以 score-v3.json 為準。沒有重跑 Actor、修交付或更動防毒設定。證據：defender-fixture-events.json、runs/nodebb-images/B1/environment-interference.json、fixture-recovery-complete.json。\n'
    report.write_text(text,encoding='utf-8')
    print(json.dumps({'stage':'comparison_report_completed','contract':judgment,'paired':paired,'environment_interference':infra},ensure_ascii=False))

if __name__=='__main__':main()
