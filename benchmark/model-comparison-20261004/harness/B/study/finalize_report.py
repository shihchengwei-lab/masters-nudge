"""Align reported costs to the complete matched cohort and retain prior B reference."""
from pathlib import Path
from collections import Counter
import hashlib, json
ROOT=Path(__file__).resolve().parent
PRIOR=Path(r'E:\masters-nudge-benchmark\sol61-b-required-structure-12case-20261001')
summary=json.loads((ROOT/'results-summary.json').read_text(encoding='utf-8'))
text=(ROOT/'REPORT.zh-TW.md').read_text(encoding='utf-8')
count=summary['matched_usage_comparison']['pair_count']
for key,label in [('uncached_input_tokens','未快取輸入'),('cached_input_tokens','快取輸入'),('output_tokens','輸出')]:
    a=summary['arms']['A']['tokens'][key];b=summary['arms']['B']['tokens'][key]
    ma=summary['matched_usage_comparison']['arms']['A'][key];mb=summary['matched_usage_comparison']['arms']['B'][key]
    text=text.replace(f'| {label} Token（Actor＋Provider） | {a:,} | {b:,} |',f'| {label} Token（完整用量的 {count} 對，Actor＋Provider） | {ma:,} | {mb:,} |')
text=text.replace('若有缺漏，表內 Token 是已記錄用量。',f'表內 Token 使用雙方用量齊全的 {count} 對；時間與完成率仍使用全部24對。')
text=text.replace('原表內 Token 合計為已記錄部分，用量完整配對的 A／B 合計見 results-summary.json 的 matched_usage_comparison。',f'表內 Token 使用雙方用量齊全的 {count} 對；同組合計見 results-summary.json 的 matched_usage_comparison。')
prior=json.loads((PRIOR/'results-summary.json').read_text(encoding='utf-8'))
current={(r['case'],r['arm']):r for r in summary['deliveries'] if r['arm'].startswith('B')}
before={(r['case'],r['arm']):r for r in prior['deliveries'] if r['arm'].startswith('B')}
labels=Counter('新增完成' if n['completed'] and not before[k]['completed'] else '失去完成' if not n['completed'] and before[k]['completed'] else '同樣完成' if n['completed'] else '同樣失敗' for k,n in current.items())
source=PRIOR/'results-summary.json'
comparison={'scope':'Historical B content/result reference, not a simultaneous new arm','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'old_completed':prior['arms']['B']['completed'],'new_completed':summary['arms']['B']['completed'],'counts':dict(labels),'cases':[{'case':k[0],'arm':k[1],'old_completed':before[k]['completed'],'new_completed':n['completed']} for k,n in current.items()]}
(ROOT/'previous-B-comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
text+='\n## 與前次 B 的歷史對比\n\n'
text+=f'前次B完成 {comparison["old_completed"]}/24；本次B完成 {comparison["new_completed"]}/24。依同題同次對應：'+ '、'.join(f'{k}{v}份' for k,v in labels.items())+'。原B封存結果只作歷史參考；沒有重評或覆寫。詳見 previous-B-comparison.json。\n'
text+='\n## 本次凍結設定\n\n定稿提示 semantic SHA256：`e67172b2e0daa982139a2c99b1656b6e01982ec7ee54d96193395e3763eb0214`；四欄上限40／25／61／35、總上限200。檔案來源資訊已包含於工具套件。每題兩次，全新B24份；Actor／Provider均GPT-6.1 Sol medium，最多三則送達提醒，兩次沉默停止。固定驗收、執行規則與匿名品味評審沿用原流程。執行失敗、超時與原始輸出保留；沒有依品質或完成結果重抽。\n'
(ROOT/'REPORT.zh-TW.md').write_text(text,encoding='utf-8')
print(json.dumps({'matched_usage_pairs':count,'prior_B_reference':dict(labels)},ensure_ascii=False))
