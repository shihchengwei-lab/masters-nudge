"""Reuse the established B-only experiment with the user-finalized package."""
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
PRIOR=Path(r'E:\masters-nudge-benchmark\sol61-b-required-structure-12case-20261001')
assert not (ROOT/'run.py').exists(), 'Setup already completed'
for name in ['run.py','finish.py','review.py','blind.py','complete_report.py','live.py']:
    text=(PRIOR/name).read_text(encoding='utf-8')
    if name=='run.py':
        text=text.replace("PROMPT_HASH = '19fb55df1c5f48fd4bdf51db2b38f508c59d3f2b6fa16f566dac75328aa48a45'", "PROMPT_HASH = 'e67172b2e0daa982139a2c99b1656b6e01982ec7ee54d96193395e3763eb0214'")
        text=text.replace('Fresh B 12 cases x 2, required/structure and flow projection; archived Sol61 A comparison', 'Fresh B 12 cases x 2, finalized data/distinctions/information prompt and file-origin facts; archived Sol61 A comparison')
        text=text.replace('24 fresh B trials using current required/structure package; maximum three delivered nudges.', '24 fresh B trials using the finalized package with file-origin facts and 40/25/61/35 field limits; maximum three delivered nudges.')
    if name=='finish.py':
        text=text.replace('B 使用本次 REQUIRED／STRUCTURE 版本全新實作。', 'B 使用2026-10-01定稿的責任／資料區別／資訊版本全新實作。')
    (ROOT/name).write_text(text,encoding='utf-8')

verify=(PRIOR/'verify_final.py').read_text(encoding='utf-8')
verify=verify.replace("assert len(blind) == summary['taste_jointly_completed_pairs'] == 6", "assert len(blind) == summary['taste_jointly_completed_pairs'] == sum(a['completed'] is True and b['completed'] is True for a in summary['deliveries'] if a['arm'].startswith('A') for b in summary['deliveries'] if b['case']==a['case'] and b['arm']=='B'+a['arm'][1:])")
verify=verify.replace("assert summary['matched_usage_comparison']['pair_count'] == 22", "assert summary['matched_usage_comparison']['pair_count'] == sum(a['actor_usage_available'] and b['actor_usage_available'] for a in summary['deliveries'] if a['arm'].startswith('A') for b in summary['deliveries'] if b['case']==a['case'] and b['arm']=='B'+a['arm'][1:])")
old="assert summary['paired_contract_results'] == {'B_only_completed': 2, 'A_only_completed': 0,\n                                             'both_completed': 6, 'both_failed': 16, 'unresolved': 0}"
new="assert sum(summary['paired_contract_results'].values()) == 24\nassert summary['paired_contract_results']['unresolved'] == 0\nassert summary['paired_contract_results']['both_completed'] == len(blind)"
assert old in verify
verify=verify.replace(old,new)
verify=verify.replace("'jointly_completed_taste_pairs': 6", "'jointly_completed_taste_pairs': len(blind)")
verify=verify.replace("'matched_usage_pairs': 22", "'matched_usage_pairs': summary['matched_usage_comparison']['pair_count']")
(ROOT/'verify_final.py').write_text(verify,encoding='utf-8')
print('Prepared the unchanged execution/grading flow; removed only prior-result constants from reporting checks.')
