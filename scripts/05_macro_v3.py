# -*- coding: utf-8 -*-
"""Macro-level (v3): identity-family mentions per page (both editions = 297 pages, same layout).
Cleanest cross-version normalization. Renders Figure 1."""
import json
import re
import numpy as np

BASE = r'C:\Users\1\Desktop\韩国国防白皮书\_tmp_hssc'

KO_A = '한미동맹|동맹|연합방위|확장억제|한미 연합|한미합동|연합훈련|연합연습|전략동맹|한미안보|연합군사|연합작전|주한미군'
KO_G = '국제평화|세계평화|PKO|국제사회|중추국가|글로벌|유엔|다국적|국제적|세계적|국제비확산|국제군축|국제'
KO_P = '평화통일|비핵화|평화적|대화|평화 정착|평화구축|평화 유지|영구적 평화|평화롭|남북|군축|화해|담대한 구상|평화'
EN_A = r'alliance|allied|combined defense|combined defence|extended deterrence|ROK[- ]U\.?S\.|U\.?S\.[- ]ROK|joint exercise|joint training|combined exercise|joint statement|strategic alliance|comprehensive strategic|USFK|U\.S\. Forces Korea|combined forces|joint operational|combined maritime'
EN_G = r'international|world peace|PKO|peacekeeping|international community|pivotal state|global|United Nations|\bUN\b|multinational'
EN_P = r'peaceful reunification|denuclearization|peaceful|dialogue|peace|inter-Korean|arms control|reconciliation|Bold Initiative'

ko = json.load(open(BASE + '\\ko_sentences.json', encoding='utf-8'))
en = json.load(open(BASE + '\\en_sentences.json', encoding='utf-8'))
N_PAGES = 297

KA, KG, KP = (re.compile(x) for x in [KO_A, KO_G, KO_P])
EA, EG, EP = (re.compile(x, re.I) for x in [EN_A, EN_G, EN_P])

def per_page(sents, rxs):
    counts = [sum(len(rx.findall(s['text'])) for rx in rxs) for s in sents]
    return sum(counts) / N_PAGES, sum(counts)

koA, koAn = per_page(ko, [KA]); koP, koPn = per_page(ko, [KP]); koG, koGn = per_page(ko, [KG])
enA, enAn = per_page(en, [EA]); enP, enPn = per_page(en, [EP]); enG, enGn = per_page(en, [EG])

print('family        KO total  KO/page   EN total  EN/page   ratio EN/KO')
for name, (kt, kp_, et, ep_) in [('Alliance', (koAn, koA, enAn, enA)), ('Peace', (koPn, koP, enPn, enP)), ('Global', (koGn, koG, enGn, enG))]:
    print('%-10s %7d %9.2f %9d %9.2f %9.2f' % (name, kt, kp_, et, ep_, ep_ / kp_))

macro = {
    'normalization': 'mentions per page (297 pages in both editions)',
    'ko': {'alliance_total': koAn, 'alliance_per_page': round(koA, 2), 'peace_total': koPn, 'peace_per_page': round(koP, 2), 'global_total': koGn, 'global_per_page': round(koG, 2)},
    'en': {'alliance_total': enAn, 'alliance_per_page': round(enA, 2), 'peace_total': enPn, 'peace_per_page': round(enP, 2), 'global_total': enGn, 'global_per_page': round(enG, 2)},
}
json.dump(macro, open(BASE + '\\macro_results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fam_names = ['Alliance-centrality', 'Peninsular peace', 'Global contribution']
kv = [koA, koP, koG]
ev = [enA, enP, enG]
x = np.arange(3)
w = 0.36
fig, ax = plt.subplots(figsize=(7.0, 3.4))
b1 = ax.bar(x - w / 2, kv, w, label='Korean original (KO-SOURCE)', color='#4C72B0')
b2 = ax.bar(x + w / 2, ev, w, label='Official English (EN-OFF)', color='#DD8452')
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3, '%.1f' % b.get_height(), ha='center', va='bottom', fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(fam_names, fontsize=9.5)
ax.set_ylabel('Marker mentions per page', fontsize=9.5)
ax.set_ylim(0, max(max(kv), max(ev)) * 1.22)
ax.legend(fontsize=9, frameon=False)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(BASE + '\\fig1_thematic.png', dpi=300)
print('fig1 saved (per-page grouped bars)')
