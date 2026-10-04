"""Recompute the seven-arm report from bundled records. Standard library only.

python -X utf8 aggregate.py           # rebuild tables, CSV and report
python -X utf8 aggregate.py --verify  # verify the bundle and generated outputs
Neither command runs models, modifies deliveries, or needs the original drives.
"""
from pathlib import Path
from collections import Counter
from itertools import combinations
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent
ARMS = 'ABCDEFI'
PAIR_SOURCES = {'A-B': 'B', 'A-C': 'C', 'B-C': 'C', 'A-D': 'D',
                'B-D': 'D', 'D-E': 'E', 'C-F': 'F', 'E-F': 'F', 'C-I': 'I', 'F-I': 'I'}
NAMES = {'A': 'Sol medium 直接做', 'B': 'Sol medium＋Sol medium',
         'C': 'Sol xhigh 直接做', 'D': 'Sol medium＋Astra medium',
         'E': 'Sol xhigh＋Astra medium', 'F': 'Sol xhigh＋Sol medium', 'I': 'Sol xhigh＋Sol xhigh'}
CASE_NOTES = {
    'nodebb-images': ('JavaScript', '依擁有者與圖片類別刪除全部相關檔案，保留其他人的檔案與原介面行為。'),
    'ansible-type-tags': ('Python', '型別轉換保留信任與來源標記，正確處理布林、位元組、序列、映射及空值。'),
    'element-sessions': ('TypeScript／React', '多裝置勾選、計數、取消與單次批次登出；篩選切換、刷新及驗證取消保持一致。'),
    'flipt-segments': ('Go', '支援單一／多分群的匯入、匯出與儲存，保留 rollout 原有格式與既有行為。'),
    'openlibrary-index-state': ('Python', '按作品、作者、版本分別更新索引，處理孤立版本，並回傳可檢查的新增與刪除結果。'),
    'proton-mailbox-retry': ('TypeScript／React', '修改操作期間暫緩抓取；失敗與陳舊回應需重試，保留未完成刷新與載入狀態。'),
    'flipt-storage-cache': ('Go', '讓儲存層查詢也使用快取，識別 no-store 請求並禁止寫入快取。'),
    'fb-metaflow-stubs': ('Python', '由執行時物件產生型別描述檔，保留類別、函式簽名、註記、overload 與模組狀態。'),
    'tracing-1523': ('Rust', '各記錄層有獨立過濾視圖，包含巢狀關係、事件、span、上下文與快取判斷。'),
    'proton-untrusted-keys': ('TypeScript／React', '區分固定與不可信金鑰的加密偏好，保留使用者關閉選擇、預設行為、儲存與上傳。'),
    'regexp-404': ('TypeScript／JavaScript', '把字元集合納入重複分支分析，保持比對方向、順序與安全修正行為。'),
    'clap-2297': ('Rust', '按每次參數出現分組取得值，正確處理自我覆寫，保留既有出現次數語意。'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def ranking(values, higher=True):
    groups = {}
    for arm, value in values.items():
        groups.setdefault(value, []).append(arm)
    return ' > '.join(' = '.join(sorted(groups[value]))
                      for value in sorted(groups, reverse=higher))


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '|' + '|'.join('---' for _ in headers) + '|']
                     + ['| ' + ' | '.join(str(cell) for cell in row) + ' |' for row in rows])


def original_pairs(cases, summaries):
    """Check raw per-judge outputs and majority decisions, not just old summaries."""
    pairs = {}
    with zipfile.ZipFile(ROOT / 'evidence.zip') as archive:
        for name, source in PAIR_SOURCES.items():
            rows = []
            for cid in cases:
                for trial in (1, 2):
                    prefix = f'judges/{source}/{cid}/trial-{trial}/{name}/'
                    pair = json.loads(archive.read(prefix + 'pair.json'))
                    expected = next(row for row in summaries[source]['pairs']
                                    if row.get('pair', 'A-B') == name and row['case'] == cid and row['trial'] == trial)
                    assert pair == expected
                    if pair['status'] != 'blind_complete':
                        continue
                    judges = pair['judges']
                    for number, judge in enumerate(judges, 1):
                        assert judge == json.loads(archive.read(prefix + f'judge-{number}/result.json'))
                        output = json.loads(archive.read(prefix + f'judge-{number}/output.json'))
                        assert all(judge[key] == value for key, value in output.items())
                        assert judge['model'] == 'gpt-6-astra' and judge['reasoning'] == 'medium'
                        mapped = 'tie' if judge['winner'] == 'tie' else judge['mapping'][judge['winner']][0]
                        assert mapped == judge['winner_arm']
                    assert judges[0]['mapping']['X'] == judges[1]['mapping']['Y']
                    assert judges[0]['mapping']['Y'] == judges[1]['mapping']['X']
                    assert len(judges) == (2 if judges[0]['winner_arm'] == judges[1]['winner_arm'] else 3)
                    counts = Counter(judge['winner_arm'] for judge in judges)
                    winner = next((arm for arm in (*name.split('-'), 'tie') if counts[arm] >= 2), 'tie')
                    assert pair['winner'] == winner
                    rows.append(pair)
            pairs[name] = rows
    return pairs


def compute():
    plans = {arm: read(ROOT / 'data/plans' / (arm + '.json')) for arm in ARMS}
    cases = list(plans['F']['cases'])
    assert len(cases) == 12
    assert all(list(plan['cases']) == cases for plan in plans.values())
    assert len({plan['evaluator_sha256'] for plan in plans.values()}) == 1
    assert all(plans[arm]['package_hashes'] == plans['B']['package_hashes'] for arm in 'DEF')
    changed = [name for name, value in plans['I']['package_hashes'].items()
               if value != plans['F']['package_hashes'][name]]
    assert changed == ['masters_nudge/runtime.py']
    standard_runtime = (ROOT / 'protocol/nudge-plugin/masters_nudge/runtime.py').read_bytes()
    experiment_runtime = (ROOT / 'protocol/nudge-plugin-I/masters_nudge/runtime.py').read_bytes()
    assert experiment_runtime == standard_runtime.replace(b'PROVIDER_REASONING_EFFORT = "medium"', b'PROVIDER_REASONING_EFFORT = "xhigh"')
    assert len({plans[arm]['prompt_semantic_sha256'] for arm in 'BDEFI'}) == 1
    assert len({plans[arm]['codex_binary_sha256'] for arm in 'ABC'}) == 1
    assert len({plans[arm]['codex_binary_sha256'] for arm in 'DEFI'}) == 1
    summaries = {arm: read(ROOT / 'data/summaries' / (arm + '.json')) for arm in 'BCDEFI'}
    records = {}
    with zipfile.ZipFile(ROOT / 'evidence.zip') as archive:
        for filename, expected_count in (('continuation-preserved-results.json', 17),
                                         ('grading-resume-preserved-results.json', 24)):
            preserved = read(ROOT / 'data/provenance/I' / filename)
            assert len(preserved) == expected_count
            for relative, expected in preserved.items():
                member = relative.replace('\\', '/').replace('runs/', 'runs/I/', 1)
                assert digest(archive.read(member)) == expected, relative
        for cid in cases:
            prompt_hashes = set()
            for arm in ARMS:
                for trial in (1, 2):
                    slot = arm + str(trial)
                    prefix = f'runs/{arm}/{cid}/{slot}/'
                    result = json.loads(archive.read(prefix + 'result.json'))
                    score = json.loads(archive.read(prefix + 'score-v3.json'))
                    launch = json.loads(archive.read(prefix + 'launch.json'))
                    assert digest(archive.read(prefix + 'final.patch')) == result['patch_sha256'] == score['patch_sha256']
                    prompt = archive.read(prefix + 'prompt.txt').decode('utf-8').replace('\r\n', '\n')
                    prompt_hashes.add(digest(prompt.encode('utf-8')))
                    assert result['base_commit'] == plans[arm]['cases'][cid]['base_commit']
                    effort = 'xhigh' if arm in 'CEFI' else 'medium'
                    provider = 'gpt-6.1-sol' if arm in 'BFI' else 'gpt-6-astra' if arm in 'DE' else None
                    assert result['actor_model'] == launch['model'] == 'gpt-6.1-sol'
                    assert result['actor_reasoning'] == launch['reasoning'] == effort
                    command = launch['command']
                    assert command[0] == plans[arm]['codex_binary']
                    assert command[command.index('-m') + 1] == 'gpt-6.1-sol'
                    assert 'model_reasoning_effort="' + effort + '"' in command
                    assert result['provider_model'] == provider
                    assert result['provider_reasoning'] == ('xhigh' if arm == 'I' else 'medium' if provider else None)
                    assert bool(launch['hooks']) == bool(provider)
                    assert launch['timeout_seconds'] == 1800
                    assert result['provider_delivered_count'] <= 3
                    assert score['evaluator_sha256'] == plans[arm]['evaluator_sha256']
                    actor = result.get('actor_usage') or {}
                    advisor = result.get('provider_usage') or {}
                    tokens = {key: int(actor.get(key, 0)) + int(advisor.get(key, 0))
                              for key in ('input_tokens', 'cached_input_tokens', 'output_tokens')}
                    tokens['uncached_input_tokens'] = tokens['input_tokens'] - tokens['cached_input_tokens']
                    records[cid, slot] = {
                        'case': cid, 'arm': slot, 'frozen_completed': score['task_completed'],
                        'completed': score['task_completed'], 'functional_pass': score['status'] == 'pass',
                        'fixed_status': score['status'], 'execution_status': score['execution_contract_status'],
                        'failed_checks': score['failed_checks'], 'confirmed_original_clause_gaps': [],
                        'seconds': result['actor_elapsed_seconds'], 'tokens': tokens,
                        'actor_usage_available': bool(actor), 'provider_feedback': result['provider_delivered_count'],
                        'provider_attempts': result['provider_attempt_count'], 'provider_silences': result['provider_silence_count'],
                        'provider_faults': result['provider_fault_count'], 'fault': result['execution_fault'],
                        'patch_sha256': result['patch_sha256'], 'evidence_prefix': prefix,
                    }
            assert len(prompt_hashes) == 1, ('Actor prompts differ', cid)
    assert len(records) == 168
    index = read(ROOT / 'source-index.json')
    receipt = read(ROOT / 'data/provenance/I/collection-extension.json')
    previous_index = encoded(index[:receipt['previous_source_files']])
    assert receipt['previous_source_index_sha256'] in (
        digest(previous_index), digest(previous_index.replace(b'\n', b'\r\n')))
    indexed_sources = {row['source']: row['sha256'] for row in index}
    for source, expected in plans['I']['reference_manifest'].items():
        assert indexed_sources[source] == expected, source
    timeout = records['tracing-1523', 'I1']
    assert not timeout['completed'] and timeout['seconds'] == 1800
    assert timeout['patch_sha256'] == digest(b'') and not timeout['actor_usage_available']
    assert summaries['I']['timeout_recovery']['deadline_patch_unavailable']
    assert not summaries['I']['timeout_recovery']['actor_rerun']
    assert not summaries['I']['verification_recovery']['actor_rerun']
    diagnostic = {}
    for path in sorted((ROOT / 'data/diagnostics').glob('*.json')):
        cid = 'flipt-segments' if path.stem.endswith('flipt') else 'clap-2297'
        for row in read(path)['rows']:
            if row['arm'] == 'BASE':
                continue
            passed = row.get('contract_passed')
            if passed is None:
                passed = (len(row['probes']) == 2 and all(p['passed'] for p in row['probes'])) if cid == 'flipt-segments' else row['occurrences_preserved']
            key = cid, row['arm']
            assert row['patch_sha256'] == records[key]['patch_sha256']
            if key in diagnostic:
                assert diagnostic[key]['passed'] == passed
                assert diagnostic[key]['fixture_sha256'] == row['fixture_sha256']
            diagnostic[key] = {'passed': passed, 'source': path.relative_to(ROOT).as_posix(),
                               'fixture_sha256': row['fixture_sha256']}
    for cid in ('flipt-segments', 'clap-2297'):
        assert len({row['fixture_sha256'] for key, row in diagnostic.items() if key[0] == cid}) == 1
        assert all((cid, arm + str(trial)) in diagnostic for arm in ARMS for trial in (1, 2))
    for key, row in diagnostic.items():
        if not row['passed']:
            records[key]['completed'] = False
            records[key]['functional_pass'] = False
            records[key]['confirmed_original_clause_gaps'].append(
                'rollout legacy shape' if key[0] == 'flipt-segments' else 'existing occurrences count')

    common_usage = [(cid, trial) for cid in cases for trial in (1, 2)
                    if all(records[cid, arm + str(trial)]['actor_usage_available'] for arm in ARMS)]
    excluded = [(cid, trial) for cid in cases for trial in (1, 2) if (cid, trial) not in common_usage]
    assert len(common_usage) == 19
    common_completed = [(cid, trial) for cid in cases for trial in (1, 2)
                        if all(records[cid, arm + str(trial)]['completed'] for arm in ARMS)]
    arms = {}
    for arm in ARMS:
        rows = [records[cid, arm + str(trial)] for cid in cases for trial in (1, 2)]
        counts = {cid: sum(records[cid, arm + str(trial)]['completed'] for trial in (1, 2)) for cid in cases}
        seconds = sum(row['seconds'] for row in rows)
        completed = sum(counts.values())
        arms[arm] = {
            'name': NAMES[arm], 'recorded': 24, 'completed': completed,
            'frozen_completed': sum(row['frozen_completed'] for row in rows),
            'functional_pass_without_deadline': sum(row['functional_pass'] for row in rows),
            'cases_at_least_one_complete': sum(count > 0 for count in counts.values()),
            'cases_both_complete': sum(count == 2 for count in counts.values()),
            'case_completed_trials': counts, 'seconds': seconds,
            'minutes_per_completion_including_failures': seconds / 60 / completed,
            'execution_status': dict(Counter(row['execution_status'] for row in rows)),
            'timeouts': [row['case'] + '/' + row['arm'] for row in rows if 'exceeded 1800' in row['fault']],
            'functional_pass_but_execution_fail': [row['case'] + '/' + row['arm'] for row in rows
                                                   if row['functional_pass'] and row['execution_status'] != 'pass'],
            'provider_feedback': sum(row['provider_feedback'] for row in rows),
            'provider_faults': sum(row['provider_faults'] for row in rows),
            'received_feedback_deliveries': sum(row['provider_feedback'] > 0 for row in rows),
            'actor_usage_missing': sum(not row['actor_usage_available'] for row in rows),
            'common_19_tokens': {key: sum(records[cid, arm + str(trial)]['tokens'][key] for cid, trial in common_usage)
                                 for key in ('uncached_input_tokens', 'cached_input_tokens', 'output_tokens')},
        }
    assert {arm: row['completed'] for arm, row in arms.items()} == dict(zip(ARMS, (6, 8, 13, 8, 10, 11, 13)))
    assert all(arms[arm]['completed'] == summaries['F']['arms'][arm]['completed'] for arm in 'CEF')
    assert arms['I']['completed'] == summaries['I']['arms']['I']['completed']
    prior = read(ROOT / 'data/prior-five-arm-summary.json')
    assert all(arms[arm]['completed'] == prior['arms'][arm]['completed'] for arm in 'ABCDE')

    raw_pairs = original_pairs(cases, summaries)
    pairs = {}
    for name, source in PAIR_SOURCES.items():
        left, right = name.split('-')
        original = raw_pairs[name]
        eligible = [pair for pair in original if all(records[pair['case'], arm + str(pair['trial'])]['completed'] for arm in (left, right))]
        votes = dict(Counter(pair['winner'] for pair in eligible))
        counts = Counter()
        for cid in cases:
            for trial in (1, 2):
                x = records[cid, left + str(trial)]['completed']
                y = records[cid, right + str(trial)]['completed']
                counts['both_completed' if x and y else left + '_only' if x else right + '_only' if y else 'both_failed'] += 1
        assert counts['both_completed'] == len(eligible)
        pairs[name] = {'source_study': source, 'pairs': len(eligible), 'votes': votes,
                       'relation': left + ' > ' + right if votes.get(left, 0) > votes.get(right, 0) else right + ' > ' + left if votes.get(left, 0) < votes.get(right, 0) else left + ' = ' + right,
                       'contract_counts': dict(counts), 'eligible_pairs': eligible,
                       'excluded_original_votes': [{'case': p['case'], 'trial': p['trial'], 'winner': p['winner']} for p in original if p not in eligible],
                       'common_four_votes': dict(Counter(p['winner'] for p in eligible if (p['case'], p['trial']) in common_completed))}
    absent = [a + '-' + b for a, b in combinations(ARMS, 2) if a + '-' + b not in pairs]
    ranks = {
        'completed': ranking({arm: row['completed'] for arm, row in arms.items()}),
        'functional': ranking({arm: row['functional_pass_without_deadline'] for arm, row in arms.items()}),
        'coverage': ranking({arm: row['cases_at_least_one_complete'] for arm, row in arms.items()}),
        'repeat_completion': ranking({arm: row['cases_both_complete'] for arm, row in arms.items()}),
        'less_time': ranking({arm: row['seconds'] for arm, row in arms.items()}, False),
        'completion_efficiency': ranking({arm: row['minutes_per_completion_including_failures'] for arm, row in arms.items()}, False),
    }
    for key in ('uncached_input_tokens', 'cached_input_tokens', 'output_tokens'):
        ranks['less_' + key] = ranking({arm: row['common_19_tokens'][key] for arm, row in arms.items()}, False)
    i_comparisons = {}
    for reference in 'CF':
        slots = [(cid, trial) for cid in cases for trial in (1, 2)
                 if all(records[cid, arm + str(trial)]['actor_usage_available'] for arm in (reference, 'I'))]
        usage = {arm: {key: sum(records[cid, arm + str(trial)]['tokens'][key] for cid, trial in slots)
                       for key in ('input_tokens', 'cached_input_tokens', 'uncached_input_tokens', 'output_tokens')}
                 for arm in (reference, 'I')}
        original = summaries['I']['comparisons'][reference + '-I']['matched_usage']
        assert len(slots) == original['pair_count'] and usage == original['arms']
        i_comparisons[reference + '-I'] = {'usage_slots': len(slots), 'tokens': usage,
            'time_change_percent': (arms['I']['seconds'] / arms[reference]['seconds'] - 1) * 100,
            'token_change_percent': {key: (usage['I'][key] / usage[reference][key] - 1) * 100
                                    for key in ('uncached_input_tokens', 'cached_input_tokens', 'output_tokens')}}
    return {'arms': arms, 'deliveries': list(records.values()), 'pairs': pairs, 'rankings': ranks,
            'common_usage_pairs': common_usage, 'excluded_usage_pairs': excluded,
            'common_completed_pairs': common_completed, 'unmeasured_taste_pairs': absent,
            'diagnostics': [{'case': key[0], 'arm': key[1], **value} for key, value in diagnostic.items()],
            'grading_separate': {arm: summaries[arm]['grading_cost_separate'] for arm in 'BCDEFI'},
            'I_comparisons': i_comparisons,
            'I_execution_repairs': {key: summaries['I'][key] for key in ('infrastructure_recovery', 'timeout_recovery', 'verification_recovery')},
            'preservation_verified': {'original_A_F_source_files': receipt['previous_source_files'],
                                      'I_before_continuation_results': 17, 'I_before_grading_results': 24,
                                      'I_reference_source_files': len(plans['I']['reference_manifest'])},
            'new_actors': 0, 'new_judges': 0}


def render(summary):
    arms = summary['arms']
    cases = read(ROOT / 'protocol/evaluation/cases.json')
    case_map = {case['id']: case for case in cases}
    changes = {
        'RANK_COMPLETED': summary['rankings']['completed'],
        'RANK_FUNCTIONAL': summary['rankings']['functional'],
        'RANK_COVERAGE': summary['rankings']['coverage'],
        'RANK_REPEAT': summary['rankings']['repeat_completion'],
        'RANK_TIME': summary['rankings']['less_time'],
        'RANK_EFFICIENCY': summary['rankings']['completion_efficiency'],
        'RANK_INPUT': summary['rankings']['less_uncached_input_tokens'],
        'RANK_CACHED': summary['rankings']['less_cached_input_tokens'],
        'RANK_OUTPUT': summary['rankings']['less_output_tokens'],
        'CONTRACT_TABLE': table(['臂', '完整交付', '至少一次完成的題數', '兩次都完成的題數', '累計分鐘', '每完成一份的分鐘'],
            [[arm, f"{row['completed']}/24（{row['completed']/24:.1%}）", f"{row['cases_at_least_one_complete']}/12", f"{row['cases_both_complete']}/12", f"{row['seconds']/60:.1f}", f"{row['minutes_per_completion_including_failures']:.1f}"] for arm, row in arms.items()]),
        'CASE_TABLE': table(['題目／完整契約', '來源專案', '語言', '主要交付要求'],
            [[f"[{cid}](protocol/evaluation/cases/{cid}/task.md)", f"[{case_map[cid]['repository']}]({case_map[cid]['source']})", *CASE_NOTES[cid]] for cid in arms['A']['case_completed_trials']]),
        'CASE_RESULTS': table(['題目', *ARMS], [[cid, *[str(arms[arm]['case_completed_trials'][cid]) + '/2' for arm in ARMS]] for cid in arms['A']['case_completed_trials']]),
        'TOKEN_TABLE': table(['臂', '未快取輸入 Token', '快取輸入 Token', '輸出 Token'],
            [[arm, *[f"{row['common_19_tokens'][key]:,}" for key in ('uncached_input_tokens', 'cached_input_tokens', 'output_tokens')]] for arm, row in arms.items()]),
        'TASTE_TABLE': table(['直接比較', '共同完整配對', '前者勝', '後者勝', '持平', '本批關係'],
            [[name, row['pairs'], row['votes'].get(name[0], 0), row['votes'].get(name[-1], 0), row['votes'].get('tie', 0), row['relation']] for name, row in summary['pairs'].items()]),
        'NUDGE_TABLE': table(['臂', '收到提醒的交付', '送達提醒', 'Provider 故障', '執行規則通過', '超時'],
            [[arm, f"{row['received_feedback_deliveries']}/24", row['provider_feedback'], row['provider_faults'], f"{row['execution_status'].get('pass',0)}/24", len(row['timeouts'])] for arm, row in arms.items()]),
        'SCORE_TABLE': table(['臂', '原凍結完成', '相容性補查後完整交付', '功能通過、不計交付時間'],
            [[arm, row['frozen_completed'], row['completed'], row['functional_pass_without_deadline']] for arm, row in arms.items()]),
        'GRADING_TABLE': table(['新增研究', '評審呼叫', '累計分鐘', '輸入 Token', '快取輸入 Token', '輸出 Token'],
            [[arm, row['calls'], f"{row['seconds']/60:.1f}", *[f"{row['tokens'][key]:,}" for key in ('input_tokens','cached_input_tokens','output_tokens')]] for arm, row in summary['grading_separate'].items()]),
        'COMMON_FOUR': table(['直接比較', '前者勝', '後者勝', '持平'],
            [[name, row['common_four_votes'].get(name[0], 0), row['common_four_votes'].get(name[-1], 0), row['common_four_votes'].get('tie', 0)] for name, row in summary['pairs'].items()]),
        'UNMEASURED_PAIRS': '、'.join(summary['unmeasured_taste_pairs']),
        'I_COST_TABLE': table(['I 相對', '完整交付變化', 'I 勝／對方勝／持平', '24 份時間變化', 'Token 配對數', '未快取輸入變化', '快取輸入變化', '輸出變化'],
            [[ref, arms['I']['completed'] - arms[ref]['completed'],
              '/'.join(str(summary['pairs'][ref + '-I']['votes'].get(a, 0)) for a in ('I', ref, 'tie')),
              f"{row['time_change_percent']:+.1f}%", row['usage_slots'],
              *[f"{row['token_change_percent'][key]:+.1f}%" for key in ('uncached_input_tokens', 'cached_input_tokens', 'output_tokens')]]
             for ref in 'CF' for row in [summary['I_comparisons'][ref + '-I']]]),
    }
    text = (ROOT / 'REPORT.template.zh-TW.md').read_text(encoding='utf-8')
    for key, value in changes.items():
        text = text.replace('{{' + key + '}}', value)
    assert not re.search(r'\{\{[A-Z_]+\}\}', text)
    return text.encode('utf-8')


def outputs(summary):
    output = {'results-summary.json': encoded(summary), 'REPORT.zh-TW.md': render(summary)}
    buffer = io.StringIO(newline='')
    headers = ['case', 'arm', 'frozen_completed', 'completed', 'functional_pass', 'execution_status',
               'seconds', 'provider_feedback', 'provider_faults', 'actor_usage_available',
               'failed_checks', 'confirmed_original_clause_gaps', 'patch_sha256']
    writer = csv.DictWriter(buffer, fieldnames=headers)
    writer.writeheader()
    for row in summary['deliveries']:
        writer.writerow({key: json.dumps(row[key], ensure_ascii=False) if isinstance(row[key], list) else row[key] for key in headers})
    output['deliveries.csv'] = buffer.getvalue().encode('utf-8-sig')
    return output


def verify_sources(include_originals=False):
    collection = read(ROOT / 'collection.json')
    assert sha(ROOT / 'evidence.zip') == collection['evidence_zip_sha256']
    index = read(ROOT / 'source-index.json')
    assert collection['records'] == 168
    assert collection['original_sources_unchanged'] == len(index)
    with zipfile.ZipFile(ROOT / 'evidence.zip') as archive:
        for row in index:
            actual = digest(archive.read(row['zip_member'])) if 'zip_member' in row else sha(ROOT / row['bundle_path'])
            assert actual == row['sha256'], row
            if include_originals:
                assert sha(Path(row['source'])) == row['sha256'], row['source']
    return len(index)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--originals', action='store_true', help='Also check the original local source files; original drives required.')
    args = parser.parse_args()
    count = verify_sources(args.originals)
    summary = compute()
    expected = outputs(summary)
    for name, content in expected.items():
        if args.verify:
            assert (ROOT / name).read_bytes() == content, 'Generated output differs: ' + name
        else:
            (ROOT / name).write_bytes(content)
    integrity = {'deliveries': len(summary['deliveries']), 'source_files_verified': count, 'common_usage_slots': 19,
                 'taste_direct_comparisons': len(summary['pairs']), 'new_actors': 0, 'new_judges': 0,
                 'evidence_zip_sha256': sha(ROOT / 'evidence.zip'),
                 'outputs': {name: digest(content) for name, content in expected.items()},
                 'aggregate_source_sha256': sha(ROOT / 'aggregate.py'),
                 'report_template_sha256': sha(ROOT / 'REPORT.template.zh-TW.md'),
                 'source_index_sha256': sha(ROOT / 'source-index.json'),
                 'collection_sha256': sha(ROOT / 'collection.json'),
                 'collect_source_sha256': sha(ROOT / 'collect.py'),
                 'harness_document_sha256': sha(ROOT / 'HARNESS.zh-TW.md'),
                 'package_metadata_sha256': sha(ROOT / 'package.json'),
                 'collection_extension_sha256': sha(ROOT / 'data/provenance/I/collection-extension.json')}
    if args.verify:
        assert read(ROOT / 'integrity.json') == integrity
    else:
        (ROOT / 'integrity.json').write_bytes(encoded(integrity))
    print(json.dumps({'verified': True, 'completed': {arm: row['completed'] for arm, row in summary['arms'].items()},
                      'rankings': summary['rankings'], 'taste': {name: row['relation'] for name, row in summary['pairs'].items()},
                      'source_files': count}, ensure_ascii=False))


if __name__ == '__main__':
    main()
