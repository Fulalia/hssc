# -*- coding: utf-8 -*-
"""Step 2: classify KO sentences into three attested identity axes.

Axes (empirically grounded in the 2022 DWP vocabulary):
  A  alliance-centrality   한미동맹/동맹/연합방위/확장억제/한미 연합/전략동맹
  P  peninsular peace      평화(통일)/비핵화/대화 ... peninsular context, excl. 국제평화/세계평화
  G  global contribution   중추국가/글로벌/국제평화/PKO/국제사회/세계평화 + 기여

Output: ko_identity.json  [{idx, page, text, axes:[...], dominant}]
"""
import json
import re

BASE = r'C:\Users\1\Desktop\韩国国防白皮书\_tmp_hssc'
ko = json.load(open(BASE + '\\ko_sentences.json', encoding='utf-8'))

A_PAT = re.compile('한미동맹|동맹|연합방위|확장억제|한미 연합|한미합동|연합훈련|한미일|전략동맹|포괄적 전략')
GLOBAL_PAT = re.compile('국제평화|세계평화|PKO|국제사회|국제군사협력|중추국가|글로벌|유엔|UN|국제연합|다국적|국제적 기여|세계적')
P_PAT = re.compile('평화통일|비핵화|평화적|대화|한반도 평화|평화 정착|평화구축|평화 유지|영구적 평화|평화롭|남북')
GEUY_PAT = re.compile('기여')

def classify(s):
    axes = []
    g = bool(GLOBAL_PAT.search(s)) or ('기여' in s and re.search('국제|세계|평화|글로벌|UN|유엔|군사', s) is not None and '한반도' not in s and '연합' not in s)
    a = bool(A_PAT.search(s))
    # peninsular peace: peace terms NOT in global context
    p = bool(P_PAT.search(s))
    if g:
        axes.append('G')
    if a:
        axes.append('A')
    if p and not g:  # peninsular peace, not global-peace
        axes.append('P')
    return axes

out = []
for s in ko:
    axes = classify(s['text'])
    if not axes:
        continue
    dominant = axes[0] if len(axes) == 1 else None
    out.append({'idx': s['idx'], 'page': s['page'], 'text': s['text'], 'axes': axes, 'dominant': dominant})

with open(BASE + '\\ko_identity.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

from collections import Counter
c = Counter('+'.join(x['axes']) for x in out)
print('identity sentences:', len(out))
for k, v in sorted(c.items(), key=lambda t: -t[1]):
    print(k, v)
# store fullcorpus identity proportion
print('prop of all sentences: %.1f%%' % (100.0 * len(out) / len(ko)))
