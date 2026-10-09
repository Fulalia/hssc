# Data and Code for
## "Translational Refractions of National Identity in Defense Discourse: An LLM-Enhanced Critical Study of South Korea's 2022 Defense White Paper"

DOI: https://doi.org/10.5281/zenodo.23164486
Version 1.0 — 2026-10-05

## Overview

This deposit contains all textual data, analysis scripts, and outputs underlying the
study. The study compares the Korean original of the Republic of Korea's 2022 Defense
White Paper (hereafter KO-SOURCE), its official English translation (EN-OFF), and a
neutrally prompted large-language-model English translation (EN-LLM) in order to trace
how national identity claims are refracted across versions.

## Contents

### corpus/
- `ko_off_2022_main.pdf` — official Korean main text (Republic of Korea Ministry of
  National Defense, published 2023-02-16; 297 pp.; downloaded from
  https://www.mnd.go.kr/staticfile/sites/mnd/atchmnfl/pblictn/13/PBLICTNEBOOK_202303070948276600.pdf).
- `en_off_2022_main.pdf` — official English main text (Republic of Korea Ministry of
  National Defense, released 2023-07; 297 pp.; downloaded from
  https://www.mnd.go.kr/staticfile/sites/mnd/atchmnfl/pblictn/13/PBLICTNEBOOK_202307280154382000.pdf).
- `ko_sentences.json`, `en_sentences.json` — page-anchored sentence segmentations
  produced by `01_build_corpus.py`.
- `sample150.json` — the proportional stratified random sample of 150
  identity-bearing Korean sentences (seed = 20260216, the official publication date).
- `en_llm_translations.tsv` — the EN-LLM arm: one English translation per sampled
  sentence, produced with the neutral prompt documented in the manuscript
  (see MANIFEST.txt for provenance).

### scripts/ (numbered in execution order)
- `01_build_corpus.py` — PDF text extraction, cleaning, sentence segmentation.
- `02_classify_identity.py` — identity-family classification of Korean sentences
  (attested keyword dictionaries).
- `03_draw_sample.py` — prose filter + stratified sampling (seed 20260216).
- `04_analyze_main.py` — LaBSE alignment of each sampled sentence to EN-OFF,
  cosine similarities for EN-OFF and EN-LLM, descriptives, Wilcoxon test.
- `05_macro_v3.py` — full-text identity-family marker densities per page (Fig. 1).
- `06_analyze_shift.py` — paired marker add/drop analysis (EN-OFF vs KO; EN-LLM vs KO)
  and Fig. 2.
- `labse_embed.py` — direct LaBSE embedder (transformers implementation).
- `requirements.txt`

### outputs/
- `pairs_aligned.json` — all 150 aligned quadruples (KO, EN-OFF, EN-LLM, page anchors,
  axis labels, both cosine similarities). The transparency master file.
- `analysis_results.json` — similarity statistics and tests.
- `macro_results.json` — per-page family densities.
- `shift_results.json` — marker-shift counts and case lists.
- `dropped_pairs_qc.json` — pairs excluded by the alignment QC rule (documented).

### figures/
- `fig1_thematic.png` — Figure 1 (300 dpi).
- `fig2_similarity.png` — Figure 2 (300 dpi).

## Provenance of the EN-LLM arm

See `MANIFEST.txt`. Generated 2026-10-05 with a neutral translation prompt, single
pass, no post-editing. The generation prompt is reproduced verbatim in the
manuscript's Methods section and in the manifest.

## License notes

The two white paper PDFs are official publications of the Republic of Korea Ministry
of National Defense (public sector announcement material, 공공누리 type-1
attribution license). They are redistributed here unmodified for research
verification purposes with attribution. Derived datasets and scripts: CC-BY 4.0.

## Reproduction

```
pip install -r scripts/requirements.txt
python scripts/01_build_corpus.py
python scripts/02_classify_identity.py
python scripts/03_draw_sample.py
python scripts/04_analyze_main.py
python scripts/05_macro_v3.py
python scripts/06_analyze_shift.py
```
The LaBSE checkpoint (sentence-transformers/LaBSE) is fetched automatically or can be
placed in `labse_model/`.
