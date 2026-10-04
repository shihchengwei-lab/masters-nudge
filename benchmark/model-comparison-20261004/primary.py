"""Rebuild the post-study nine-task comparison; never alter original records."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDED = ('fb-metaflow-stubs', 'tracing-1523', 'regexp-404')
ARMS = 'ABCDEFI'
KEYS = ('uncached_input_tokens', 'cached_input_tokens', 'output_tokens')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def compute():
    original = read(ROOT / 'results-summary.json')
    rows = [r for r in original['deliveries'] if r['case'] not in EXCLUDED]
    assert len(rows) == 126
    assert not any(r['completed'] for r in original['deliveries'] if r['case'] in EXCLUDED)
    cases = list(dict.fromkeys(r['case'] for r in rows))
    by_slot = {(r['case'], r['arm']): r for r in rows}
    slots = [(c, t) for c in cases for t in (1, 2)
             if all(by_slot[c, a + str(t)]['actor_usage_available'] for a in ARMS)]
    arms = {}
    for arm in ARMS:
        selected = [r for r in rows if r['arm'][0] == arm]
        completed = sum(r['completed'] for r in selected)
        seconds = sum(r['seconds'] for r in selected)
        arms[arm] = {'name': original['arms'][arm]['name'], 'recorded': len(selected),
                     'completed': completed, 'seconds': seconds,
                     'minutes_per_completion_including_failures': seconds / 60 / completed,
                     'tokens': {k: sum(by_slot[c, arm + str(t)]['tokens'][k] for c, t in slots)
                                for k in KEYS}}
        assert len(selected) == 18 and completed == original['arms'][arm]['completed']
    comparisons = {}
    for left, right in [('B', 'A'), ('F', 'C'), ('I', 'C'), ('I', 'F')]:
        comparisons[left + '-' + right] = {
            'time_change_percent': (arms[left]['seconds'] / arms[right]['seconds'] - 1) * 100,
            'token_change_percent': {k: (arms[left]['tokens'][k] / arms[right]['tokens'][k] - 1) * 100
                                     for k in KEYS}}
    review = read(ROOT / 'taste-review/reassessment.json')
    return {'method': 'Post-study classification, not preregistered; original 12-task records retained.',
            'included_cases': cases, 'excluded_unresolved_cases': list(EXCLUDED),
            'deliveries': len(rows), 'attempts_per_arm': 18, 'arms': arms,
            'common_usage_slots': slots,
            'excluded_usage_slots': [(c, t) for c in cases for t in (1, 2) if (c, t) not in slots],
            'comparisons': comparisons, 'taste_pairs_unchanged': review['scope']['taste_eligible_pairs_reviewed'],
            'source_sha256': {p: sha(ROOT / p) for p in ('results-summary.json', 'taste-review/reassessment.json')},
            'new_actors': 0, 'new_judges': 0}


def render(s):
    n = len(s['common_usage_slots'])
    lines = ['# 九題主要比較', '',
             '原研究執行十二題、七種配置、每題兩次，共168次。測試後將 Regexp、Metaflow、Tracing 三題另列為未解挑戰：本研究尚無通過完整契約的實作，契約的整體可達成性尚未獲得完整實作佐證。這是事後分類，並非原始預先設定。', '',
             '**主要比較為九題，每配置18次，共126次；各臂的六次未解挑戰不計入主要完成率與成本。** 失敗與逾時仍保留在九題分母內，沒有重跑或修改答案。', '',
             '| 配置 | 完整交付 | 累計分鐘 | 每完成一份的分鐘（含失敗） |',
             '|---|---:|---:|---:|']
    for a, r in s['arms'].items():
        lines.append(f"| {a}：{r['name']} | {r['completed']}/18（{r['completed']/18:.1%}） | {r['seconds']/60:.1f} | {r['minutes_per_completion_including_failures']:.1f} |")
    lines += ['', f'時間涵蓋九題全部18次；Token 比較只使用七臂共同有完整 Actor 用量的 {n} 個同題／同次序位置，並加上各次 Provider 用量。缺失用量的位置不當作零。逐一位置見 [統計資料](primary-summary.json)。', '',
              '| 配置 | 未快取輸入 Token | 快取輸入 Token | 輸出 Token |', '|---|---:|---:|---:|']
    for a, r in s['arms'].items():
        lines.append('| ' + a + ' | ' + ' | '.join(f"{r['tokens'][k]:,}" for k in KEYS) + ' |')
    lines += ['', '| 比較（前者對後者） | 累計時間變化 | 未快取輸入變化 | 快取輸入變化 | 輸出變化 |', '|---|---:|---:|---:|---:|']
    for pair, r in s['comparisons'].items():
        lines.append('| ' + pair + ' | ' + f"{r['time_change_percent']:+.1f}%" + ' | ' + ' | '.join(f"{r['token_change_percent'][k]:+.1f}%" for k in KEYS) + ' |')
    lines += ['', '程式碼品味沿用 [覆核複評](taste-review/README.zh-TW.md) 的最終結果，共71組共同完整交付的配對。三題未解挑戰原本就沒有合格配對，因此品味母體與結果不變；不是新增盲評。', '',
              'I–F 使用相同 CLI，F/I 對 C 含 CLI 版本差異。原研究的解題時限、執行器修復、用量缺口與另列的判分／逾時後耗時見 [十二題原始報告](REPORT.zh-TW.md)；本表沿用其時間記帳，不把判分成本加到解題成本。', '',
              '九題清單：' + '、'.join(s['included_cases']) + '。', '',
              '[三題未解挑戰與 Astra max 探索](../unresolved-challenges-20261004/README.zh-TW.md)保留六份獨立答案、驗收反例、提醒採納與成本。本輪不限時探索不併入七臂排名，也不据此推算單一變因效果。', '',
              '原 [十二題數據](results-summary.json)、[CSV](deliveries.csv) 與原始證據保留。從 repo 根目錄執行 `python -X utf8 benchmark/model-comparison-20261004/primary.py --verify`，即可離線重建並核對本頁；不呼叫模型。']
    return '\n'.join(lines).replace('不据此', '不據此') + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    s = compute()
    outputs = {'primary-summary.json': json.dumps(s, ensure_ascii=False, indent=2) + '\n',
               'PRIMARY.zh-TW.md': render(s)}
    for name, text in outputs.items():
        if args.verify:
            assert (ROOT / name).read_text(encoding='utf-8') == text, name
        else:
            (ROOT / name).write_text(text, encoding='utf-8', newline='\n')
    print(json.dumps({'verified': True, 'common_usage_slots': len(s['common_usage_slots']),
                      'comparisons': s['comparisons']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
