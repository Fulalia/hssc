# -*- coding: utf-8 -*-
"""Step 3b: prose-quality filter, then proportional stratified sample of 150, seed 20260216."""
import json
import re
import random
from collections import Counter

BASE = r'C:\Users\1\Desktop\韩国国防白皮书\_tmp_hssc'
ids = json.load(open(BASE + '\\ko_identity.json', encoding='utf-8'))

def is_prose(t):
    hangul = len(re.findall(r'[가-힣]', t))
    if hangul < 30 or len(t) > 420:      # too short = fragment; too long = layout merge
        return False
    if '[도표' in t or '도표]' in t:      # figure caption/dump
        return False
    if re.search(r'\d+\.\s*$', t):        # TOC line ending with section number
        return False
    if t.count('제5장') >= 1 and '제 장' in t:  # running header merged
        return False
    return True

prose = [s for s in ids if is_prose(s['text'])]
print('identity:', len(ids), '-> prose:', len(prose))

strata = {}
for s in prose:
    strata.setdefault('+'.join(s['axes']), []).append(s)
counts = {k: len(v) for k, v in strata.items()}
print(counts)

N = 150
total = sum(counts.values())
quota = {k: round(N * n / total) for k, n in counts.items()}
drift = N - sum(quota.values())
quota[max(counts, key=counts.get)] += drift

rng = random.Random(20260216)
sample = []
for k, lst in strata.items():
    rng.shuffle(lst)
    sample.extend(lst[:quota[k]])
sample.sort(key=lambda s: s['idx'])
print('sample:', len(sample), dict(Counter('+'.join(s['axes']) for s in sample)))

with open(BASE + '\\sample150.json', 'w', encoding='utf-8') as f:
    json.dump(sample, f, ensure_ascii=False, indent=1)
batches = [sample[i:i + 15] for i in range(0, len(sample), 15)]
with open(BASE + '\\translation_workfile.txt', 'w', encoding='utf-8') as f:
    for bi, b in enumerate(batches):
        f.write('===== BATCH %d =====\n' % (bi + 1))
        for it in b:
            f.write('[%d] %s\n' % (it['idx'], it['text']))
print('batches:', len(batches), 'workfile rewritten')
