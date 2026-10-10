# Shifting Frames of Distress: Depression Metaphors in Korean Twitter Discourse (2019–2021)

Open data and verification code for the manuscript *"Shifting Frames of Distress:
Depression Metaphors in Korean Twitter Discourse Before and During the COVID-19
Pandemic"* (Frontiers in Language Sciences, revised submission).

## What this repository contains

| Path | Content |
|---|---|
| `data/corpus_descriptives.csv` | Corpus sizes, metaphor prevalence and density, tweet length, valence (Tables 3) |
| `data/domain_frequencies.csv` | Six metaphor source domains: prevalence by year, derived counts, percentage-point and relative change, mixed-effects odds ratios (Table 4) |
| `data/valence_by_domain.csv` | Mean valence (SD) by domain and year (Table 4, last columns) |
| `data/sentiment_summary.csv` | Metaphoric vs. non-metaphoric valence/arousal means (Figure 3) |
| `data/validation_performance.csv` | Domain-specific precision/recall/F1 on the held-out test set (Table 2) |
| `data/glmm_period_model.csv` | Full period-membership mixed-effects logistic model (Table 5) |
| `data/syntactic_roles.csv` | Grammatical-role coding of depression terms (Section 3.7/4.5) |
| `data/hybrid_metaphors.csv` | Cross-cluster hybrid-metaphor coding (Section 3.7/4.5) |
| `dictionary/seed_examples.csv` | Documented seed exemplars per domain (Table 1 of the manuscript) |
| `scripts/verify_consistency.py` | Reproduces every arithmetic/statistical consistency check in Supplementary Table S1 |

## Verification

```bash
python scripts/verify_consistency.py
```

The script recomputes, from the CSVs alone: all percentage-point and relative
changes; Pearson chi-square and Cramér's V for each domain and coding study;
Cohen's *d* for density and valence contrasts; the density *t*-statistic and its
degrees of freedom; β→OR conversions for the full GLMM table; and the
P/R/F1 identities for the validation table. It prints one PASS/FAIL line per
check and exits non-zero on any failure.

## What is shared and why

Raw tweet texts **cannot** be redistributed (platform terms of service and
privacy considerations for sensitive mental-health discourse). What is shared
is the complete set of aggregate quantities on which every reportable statistic
in the paper is based, plus the documented seed lists of the metaphor
dictionary, so that (a) every number in the manuscript can be audited, and
(b) the dictionary-construction procedure can be replicated for other
languages. The full 512-entry dictionary and the identification code are
maintained by the authors and available on reasonable request pending platform
terms.

## Data notes

- `n_2019`/`n_2021` in `domain_frequencies.csv` are derived from the reported
  percentages and corpus sizes (rounded to whole tweets).
- Mixed-effects odds ratios are covariate-adjusted model estimates; the
  unadjusted ratios computed from the percentages are close but need not be
  identical (see Supplementary Table S1, Section B).
- Cramér's V values are computed from the unadjusted 2×2 tests.

## Ethics

The study is a secondary, non-interventional analysis of publicly posted
content at aggregate level, with no interaction with authors, no private or
identifiable information, and no individual-level analysis; it did not undergo
institutional ethics board review (acknowledged as a limitation in the
manuscript). Only aggregate, de-identified quantities are stored in this
repository.

## License

Code: MIT. Data and dictionary seed lists: CC BY 4.0.

## Citation

See `CITATION.cff`.
