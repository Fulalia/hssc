# -*- coding: utf-8 -*-
"""Paired marker-shift analysis on the aligned 150-sentence set.
For each aligned pair (KO source vs EN-OFF official counterpart vs EN-LLM):
  - does the target sentence ADD an identity-family marker absent in the source?
  - does it DROP one present in the source?
Also renders Figure 2 (similarity by axis, paired box plot)."""
import json
import re
import numpy as np
from collections import Counter

BASE = r'C:\Users\1\Desktop\韩国国防白皮书\_tmp_hssc'

KO_A = '한미동맹|동맹|연합방위|확장억제|한미 연합|연합훈련|연합연습|전략동맹|한미안보|연합군사|연합작전|주한미군'
KO_G = '국제평화|세계평화|PKO|국제사회|중추국가|글로벌|유엔|다국적|국제적|세계적|국제비확산|국제군축|국제'
KO_P = '평화통일|비핵화|평화적|대화|평화 정착|평화구축|평화 유지|영구적 평화|평화롭|남북|군축|화해|담대한 구상|평화'
EN_A = r'alliance|alliances|allied|allies|combined defense|combined defence|extended deterrence|ROK[- ]U\.?S\.|U\.?S\.[- ]ROK|joint exercise|joint training|combined training|combined exercise|strategic alliance|comprehensive strategic|USFK|U\.S\. Forces Korea|combined forces|joint operational|combined maritime'
EN_G = r'international|world peace|PKO|peacekeeping|international community|pivotal state|global|United Nations|\bUN\b|multinational'
EN_P = r'peaceful reunification|denuclearization|peaceful|dialogue|peace|inter-Korean|arms control|reconciliation|Bold Initiative'

KA, KG, KP = (re.compile(x) for x in [KO_A, KO_G, KO_P])
EA, EG, EP = (re.compile(x, re.I) for x in [EN_A, EN_G, EN_P])
KRX = {'A': KA, 'G': KG, 'P': KP}
ERX = {'A': EA, 'G': EG, 'P': EP}

rows = json.load(open(BASE + '\\pairs_aligned.json', encoding='utf-8'))
qc = [r for r in rows if r['sim_off'] >= 0.60]
print('pairs:', len(qc))

shift = {'off': {'add': Counter(), 'drop': Counter()}, 'llm': {'add': Counter(), 'drop': Counter()}}
detail_off_add, detail_off_drop = [], []
for r in qc:
    fams_ko = {f for f, rx in KRX.items() if rx.search(r['ko'])}
    for tgt, key in [('en_off', 'off'), ('llm', 'llm')]:
        fams_en = {f for f, rx in ERX.items() if rx.search(r[tgt])}
        for f in fams_en - fams_ko:
            shift[key]['add'][f] += 1
        for f in fams_ko - fams_en:
            shift[key]['drop'][f] += 1
        if key == 'off':
            for f in fams_en - fams_ko:
                detail_off_add.append({'idx': r['idx'], 'family': f, 'ko': r['ko'][:80], 'en': r['en_off'][:80]})
            for f in fams_ko - fams_en:
                detail_off_drop.append({'idx': r['idx'], 'family': f, 'ko': r['ko'][:80], 'en': r['en_off'][:80]})

print('EN-OFF additions  :', dict(shift['off']['add']))
print('EN-OFF omissions  :', dict(shift['off']['drop']))
print('EN-LLM additions  :', dict(shift['llm']['add']))
print('EN-LLM omissions  :', dict(shift['llm']['drop']))

res = {
    'n': len(qc),
    'off_add': dict(shift['off']['add']), 'off_drop': dict(shift['off']['drop']),
    'llm_add': dict(shift['llm']['add']), 'llm_drop': dict(shift['llm']['drop']),
    'off_add_detail': detail_off_add, 'off_drop_detail': detail_off_drop,
}
json.dump(res, open(BASE + '\\shift_results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- Figure 2: paired similarity by axis ----------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

axes_single = {'A': [], 'P': [], 'G': []}
off_s = {'A': [], 'P': [], 'G': []}
for r in qc:
    if len(r['axes']) == 1:
        a = r['axes'][0]
        axes_single[a].append(r['sim_llm'])
        off_s[a].append(r['sim_off'])

names = {'A': 'Alliance', 'P': 'Peace', 'G': 'Global'}
fig, ax = plt.subplots(figsize=(7.0, 3.6))
order = ['A', 'P', 'G']
pos = np.arange(3)
w = 0.36
data_llm = [axes_single[a] for a in order]
data_off = [off_s[a] for a in order]
bp1 = ax.boxplot(data_off, positions=pos - w / 2, widths=w * 0.9, patch_artist=True,
                 boxprops=dict(facecolor='#DD8452', alpha=0.8), medianprops=dict(color='black'),
                 flierprops=dict(marker='o', markersize=3, alpha=0.5), showfliers=True)
bp2 = ax.boxplot(data_llm, positions=pos + w / 2, widths=w * 0.9, patch_artist=True,
                 boxprops=dict(facecolor='#4C72B0', alpha=0.8), medianprops=dict(color='black'),
                 flierprops=dict(marker='o', markersize=3, alpha=0.5), showfliers=True)
for i, a in enumerate(order):
    ax.text(pos[i] - w / 2, np.median(data_off[i]) - 0.035, 'med %.3f' % np.median(data_off[i]), ha='center', fontsize=7.5, color='#8a4a1f')
    ax.text(pos[i] + w / 2, np.median(data_llm[i]) - 0.035, 'med %.3f' % np.median(data_llm[i]), ha='center', fontsize=7.5, color='#25406e')
ax.set_xticks(pos)
ax.set_xticklabels([names[a] for a in order], fontsize=10)
ax.set_ylabel('LaBSE cosine similarity with source', fontsize=9.5)
ax.set_ylim(0.3, 1.02)
ax.axhline(0.70, color='grey', ls='--', lw=0.8)
ax.text(2.42, 0.705, '0.70 threshold', fontsize=7.5, color='grey')
ax.legend([bp1['boxes'][0], bp2['boxes'][0]], ['EN-OFF (official)', 'EN-LLM (LLM transfer)'], fontsize=9, frameon=False, loc='lower left')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(BASE + '\\fig2_similarity.png', dpi=300)
print('fig2 saved')
