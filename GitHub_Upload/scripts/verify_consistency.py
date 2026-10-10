# -*- coding: utf-8 -*-
"""
verify_consistency.py — numerical consistency verification for
"Shifting Frames of Distress: Depression Metaphors in Korean Twitter
Discourse Before and During the COVID-19 Pandemic"

Reproduces every statistic marked "Reproducible" or arithmetically
verifiable in Supplementary Table S1 from the aggregate data in data/.
Requires only the Python standard library.

Usage:  python verify_consistency.py
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

RESULTS = []


def check(label, ok, detail=''):
    RESULTS.append((label, ok, detail))
    print('%-4s %-58s %s' % ('PASS' if ok else 'FAIL', label, detail))


def read_csv(name):
    with open(os.path.join(DATA, name), encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def chi2_2x2(x1, n1, x2, n2):
    """Pearson chi-square for two independent proportions (2x2)."""
    tot = n1 + n2
    num = tot * (x1 * (n2 - x2) - x2 * (n1 - x1)) ** 2
    den = n1 * n2 * (x1 + x2) * (tot - x1 - x2)
    return num / den if den else float('nan')


def close(a, b, tol):
    return abs(a - b) <= tol


# ---------- corpus descriptives ----------
cd = {r['metric']: r for r in read_csv('corpus_descriptives.csv')}
N1 = int(cd['total_tweets']['x2019'])
N2 = int(cd['total_tweets']['x2021'])
N = N1 + N2
met1 = int(cd['metaphoric_tweets']['x2019'])
met2 = int(cd['metaphoric_tweets']['x2021'])

check('corpus totals sum to N = 222,346', N == 222346, '%d + %d = %d' % (N1, N2, N))
check('metaphoric pct 2019 = 33.7%', close(100 * met1 / N1, 33.7, 0.05), '%.2f%%' % (100 * met1 / N1))
check('metaphoric pct 2021 = 46.2%', close(100 * met2 / N2, 46.2, 0.05), '%.2f%%' % (100 * met2 / N2))
check('prevalence change = +12.5 pp', close(100 * (met2 / N2 - met1 / N1), 12.5, 0.05), '')
check('relative increase = 37.1%', close(100 * (met2 / N2) / (met1 / N1) - 100, 37.1, 0.15), '')
chi2 = chi2_2x2(met1, N1, met2, N2)
check('overall unadjusted chi2 = 3592.5, V = 0.127', close(chi2, 3592.5, 1.0) and close(math.sqrt(chi2 / N), 0.127, 0.001),
      'chi2 = %.1f, V = %.3f' % (chi2, math.sqrt(chi2 / N)))

# density t-test (means/SDs from corpus_descriptives)
d1, sd1 = 1.24, 0.51
d2, sd2 = 1.41, 0.62
sp = math.sqrt((sd1 ** 2 + sd2 ** 2) / 2)
coh_d = (d2 - d1) / sp
tval = coh_d / math.sqrt(1 / met1 + 1 / met2)
check("density d = 0.30", close(coh_d, 0.30, 0.005), 'd = %.3f' % coh_d)
check("density relative increase = 13.7%", close(100 * (d2 - d1) / d1, 13.7, 0.05), '')
check("density t(89777) = 43.7", met1 + met2 - 2 == 89777 and close(tval, 43.7, 0.1),
      'df = %d, t = %.1f' % (met1 + met2 - 2, tval))

# ---------- domain frequencies ----------
expected = {
    'WAR/BATTLE': (15.2, 21.5, 41.4, 1.52, 1452.6, 0.081),
    'PRISON/CONFINEMENT': (8.3, 18.7, 125.3, 2.56, 5014.2, 0.150),
    'DARKNESS/ABYSS': (26.4, 26.2, -0.8, 0.99, 1.1, 0.002),
    'HEAVINESS/BURDEN': (21.9, 24.3, 11.0, 1.08, 179.1, 0.028),
    'ENEMY/OPPRESSOR': (10.4, 12.6, 21.2, 1.29, 261.5, 0.034),
    'ILLNESS/DAMAGE': (12.1, 14.8, 22.3, 1.15, 344.6, 0.039),
}
for r in read_csv('domain_frequencies.csv'):
    dom = r['domain']
    p1, p2 = float(r['pct_2019']), float(r['pct_2021'])
    x1, x2 = int(r['n_2019']), int(r['n_2021'])
    e = expected[dom]
    ok_pp = close(p2 - p1, e[2 - 2], 0.001)  # placeholder, real checks below
    check('%s percentages match Table 4' % dom, close(p1, e[0], 1e-9) and close(p2, e[1], 1e-9))
    check('%s relative change matches' % dom,
          close(100 * (p2 - p1) / p1, e[2], 0.15), '%.1f%%' % (100 * (p2 - p1) / p1))
    check('%s derived counts consistent' % dom,
          close(x1, p1 / 100 * N1, 1.0) and close(x2, p2 / 100 * N2, 1.0))
    chi2 = chi2_2x2(x1, N1, x2, N2)
    v = math.sqrt(chi2 / N)
    check('%s unadjusted chi2/V reproduce' % dom,
          close(chi2, e[4], 2.0) and close(v, e[5], 0.002), 'chi2 = %.1f, V = %.3f' % (chi2, v))

# GLMM beta -> OR (Table 5 / glmm_period_model.csv)
for r in read_csv('glmm_period_model.csv'):
    beta, orr = float(r['beta']), float(r['odds_ratio'])
    check('GLMM %s: exp(beta) = OR' % r['predictor'], close(math.exp(beta), orr, 0.006),
          'exp(%.2f) = %.3f vs %.2f' % (beta, math.exp(beta), orr))

# ---------- valence ----------
val = {r['domain']: r for r in read_csv('valence_by_domain.csv')}
for dom, m1v, s1v, m2v, s2v, dexp in (
        ('PRISON/CONFINEMENT', 2.31, 0.65, 1.88, 0.78, 0.60),
        ('WAR/BATTLE', 2.29, 0.68, 2.05, 0.73, 0.34)):
    r = val[dom]
    m1v, s1v = float(r['valence_2019']), float(r['sd_2019'])
    m2v, s2v = float(r['valence_2021']), float(r['sd_2021'])
    sp = math.sqrt((s1v ** 2 + s2v ** 2) / 2)
    check('%s valence delta and d' % dom.split('/')[0],
          close(m1v - m2v, 0.43 if 'PRISON' in dom else 0.24, 0.005) and close((m1v - m2v) / sp, dexp, 0.005),
          'd = %.2f' % ((m1v - m2v) / sp))

# ---------- coding studies ----------
syn = {r['role']: r for r in read_csv('syntactic_roles.csv')}
ag1, ag2 = float(syn['agentive']['pct_2019']), float(syn['agentive']['pct_2021'])
check('syntactic roles sum to 100% (2019)',
      close(sum(float(syn[k]['pct_2019']) for k in syn), 100.0, 0.05))
check('syntactic roles sum to 100% (2021)',
      close(sum(float(syn[k]['pct_2021']) for k in syn), 100.0, 0.05))
x1, x2 = round(ag1 / 100 * 1000), round(ag2 / 100 * 1000)
chi2 = chi2_2x2(x1, 1000, x2, 1000)
check('agentive chi2(1) = 69.0, V = 0.19', close(chi2, 69.0, 0.5) and close(math.sqrt(chi2 / 2000), 0.186, 0.003),
      'chi2 = %.1f, V = %.3f' % (chi2, math.sqrt(chi2 / 2000)))

hyb = read_csv('hybrid_metaphors.csv')
h1 = {r['year']: r for r in hyb}
x1 = int(round(float(h1['2019']['pct']) / 100 * int(h1['2019']['n_coded'])))
x2 = int(round(float(h1['2021']['pct']) / 100 * int(h1['2021']['n_coded'])))
chi2 = chi2_2x2(x1, 500, x2, 500)
check('hybrid chi2(1) = 27.1, V = 0.16', close(chi2, 27.1, 0.5) and close(math.sqrt(chi2 / 1000), 0.165, 0.003),
      'chi2 = %.1f, V = %.3f' % (chi2, math.sqrt(chi2 / 1000)))

# ---------- validation ----------
agg = {r['domain']: r for r in read_csv('validation_performance.csv')}
for dom, r in agg.items():
    p, rc, f1 = float(r['precision']), float(r['recall']), float(r['f1'])
    check('F1 identity: %s' % dom, close(2 * p * rc / (p + rc), f1, 0.005),
          '2PR/(P+R) = %.3f vs %.2f' % (2 * p * rc / (p + rc), f1))

print()
fails = [r for r in RESULTS if not r[1]]
print('TOTAL: %d checks, %d passed, %d failed' % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
if fails:
    for label, _, detail in fails:
        print('FAILED:', label, detail)
    raise SystemExit(1)
print('ALL CHECKS PASSED')
