# -*- coding: utf-8 -*-
"""Main analysis: merge LLM translations, LaBSE alignment, similarities, thematic distribution.

Inputs : ko_sentences.json, en_sentences.json, ko_identity.json, sample150.json,
         en_llm_part1.tsv, en_llm_part2.tsv, labse_model/
Outputs: pairs_aligned.json, analysis_results.json, fig1_thematic.png, fig2_similarity.png
"""
import json
import re
import os
import numpy as np

BASE = r'C:\Users\1\Desktop\韩国国防白皮书\_tmp_hssc'
LABSE = BASE + '\\labse_model'

# ---------- 1. merge LLM translations ----------
llm = {}
for part in ['en_llm_part1.tsv', 'en_llm_part2.tsv']:
    for ln in open(BASE + '\\' + part, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if '\t' not in ln:
            continue
        idx, en = ln.split('\t', 1)
        llm[int(idx)] = en.strip()
sample = json.load(open(BASE + '\\sample150.json', encoding='utf-8'))
missing = [s['idx'] for s in sample if s['idx'] not in llm]
print('LLM translations:', len(llm), 'missing from sample:', missing)

# ---------- 2. load LaBSE (direct transformers embedder) ----------
from labse_embed import LabseEmbedder
model = LabseEmbedder(LABSE)

en_sents = json.load(open(BASE + '\\en_sentences.json', encoding='utf-8'))
en_texts = [s['text'] for s in en_sents]
print('encoding EN-OFF corpus (%d sentences)...' % len(en_texts))
en_emb = model.encode(en_texts, batch_size=64)
ko_sample_texts = [s['text'] for s in sample]
llm_texts = [llm[s['idx']] for s in sample]
ko_emb = model.encode(ko_sample_texts, batch_size=32)
llm_emb = model.encode(llm_texts, batch_size=32)

# ---------- 3. alignment + similarity (page-windowed, editions share 297-pp layout) ----------
PAGE_WIN = 3
en_pages = np.array([s['page'] for s in en_sents])
rows = []
for i, s in enumerate(sample):
    sims_en = en_emb @ ko_emb[i]
    mask = np.abs(en_pages - s['page']) <= PAGE_WIN
    sims_masked = np.where(mask, sims_en, -1.0)
    j = int(np.argmax(sims_masked))
    sim_off = float(sims_en[j])
    sim_llm = float(llm_emb[i] @ ko_emb[i])
    axes = s['axes']
    rows.append({
        'idx': s['idx'], 'page': s['page'], 'axes': axes,
        'ko': s['text'], 'en_off': en_sents[j]['text'], 'en_off_page': en_sents[j]['page'],
        'en_off_idx': j, 'sim_off': round(sim_off, 4), 'sim_llm': round(sim_llm, 4),
        'llm': llm[s['idx']],
    })

# QC: drop pairs whose EN-OFF alignment failed (similarity < 0.60 with page window)
qc_pass = [r for r in rows if r['sim_off'] >= 0.60]
qc_drop = [r for r in rows if r['sim_off'] < 0.60]
json.dump(qc_drop, open(BASE + '\\dropped_pairs_qc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('QC: aligned pairs kept %d, dropped %d' % (len(qc_pass), len(qc_drop)))
for r in qc_drop:
    print('  DROPPED idx=%d sim=%.3f ko=%s...' % (r['idx'], r['sim_off'], r['ko'][:40]))

json.dump(rows, open(BASE + '\\pairs_aligned.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 4. statistics ----------
def axis_of(r):
    a = r['axes']
    return '+'.join(a)

from collections import defaultdict
stats = defaultdict(lambda: defaultdict(list))
for r in qc_pass:
    key = axis_of(r)
    stats[key]['off'].append(r['sim_off'])
    stats[key]['llm'].append(r['sim_llm'])

report = {'n_sample': len(sample), 'n_aligned': len(qc_pass), 'n_dropped': len(qc_drop)}
print('\n=== mean similarity by stratum ===')
for k in sorted(stats):
    off = stats[k]['off']; llmv = stats[k]['llm']
    print('%-4s n=%3d  EN-OFF %.3f (sd %.3f)   EN-LLM %.3f (sd %.3f)' % (
        k, len(off), np.mean(off), np.std(off), np.mean(llmv), np.std(llmv)))
    report['stratum_' + k] = {
        'n': len(off),
        'off_mean': round(float(np.mean(off)), 3), 'off_sd': round(float(np.std(off)), 3),
        'llm_mean': round(float(np.mean(llmv)), 3), 'llm_sd': round(float(np.std(llmv)), 3),
    }

# pooled + per-axis (single-axis only for the per-axis table)
for label, keys in [('pooled', list(stats.keys())), ('A', ['A']), ('P', ['P']), ('G', ['G'])]:
    off = [x for k in keys for x in stats[k]['off']]
    llmv = [x for k in keys for x in stats[k]['llm']]
    if not off:
        continue
    report[label] = {
        'n': len(off),
        'off_mean': round(float(np.mean(off)), 3), 'off_sd': round(float(np.std(off)), 3),
        'llm_mean': round(float(np.mean(llmv)), 3), 'llm_sd': round(float(np.std(llmv)), 3),
    }
    print('%-6s n=%3d  OFF %.3f  LLM %.3f' % (label, len(off), np.mean(off), np.mean(llmv)))

# divergence counts by threshold
for th in [0.65, 0.70, 0.75]:
    d_off = sum(1 for r in qc_pass if r['sim_off'] < th)
    d_llm = sum(1 for r in qc_pass if r['sim_llm'] < th)
    report['divergence_th%.2f' % th] = {'off': d_off, 'llm': d_llm}
    print('threshold %.2f: EN-OFF divergent %d, EN-LLM divergent %d' % (th, d_off, d_llm))

# Wilcoxon signed-rank: paired off vs llm
from scipy.stats import wilcoxon
offs = [r['sim_off'] for r in qc_pass]
llms = [r['sim_llm'] for r in qc_pass]
w = wilcoxon(offs, llms)
report['wilcoxon_off_vs_llm'] = {'W': float(w.statistic), 'p': float(w.pvalue)}
print('Wilcoxon OFF vs LLM: W=%.1f p=%.2e' % (w.statistic, w.pvalue))

json.dump(report, open(BASE + '\\analysis_results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nanalysis_results.json written')
