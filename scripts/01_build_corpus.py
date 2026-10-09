# -*- coding: utf-8 -*-
"""Step 1: clean official PDF texts and split into sentences.

Outputs:
  ko_sentences.json  [{idx, page, text}]
  en_sentences.json  [{idx, page, text}]
"""
import fitz
import re
import json

BASE = r'C:\Users\1\Desktop\韩国国防白皮书\_tmp_hssc'

# ---------- page-level cleaning ----------

KILL_KO = [
    r'^\s*<<+PAGE \d+>>+\s*$',
    r'국방백서',            # running header (bare header lines)
    r'DEFENSE WHITE PAPER',
    r'^\s*-?\s*\d{1,3}\s*-?\s*$',      # bare page numbers
]
KILL_EN = [
    r'^\s*<<+PAGE \d+>>+\s*$',
    r'2022 DEFENSE WHITE PAPER',
    r'^\s*-?\s*\d{1,3}\s*-?\s*$',
]

def clean_pages(txt_path, kill_patterns):
    raw = open(txt_path, encoding='utf-8').read()
    pages = re.split(r'\n<<<PAGE (\d+)>>>\n', raw)
    # pages: ['', '1', text1, '2', text2, ...]
    out = []
    for i in range(1, len(pages), 2):
        pno = int(pages[i])
        body = pages[i + 1]
        lines = []
        for ln in body.split('\n'):
            s = ln.strip()
            if not s:
                continue
            if any(re.search(p, s) for p in kill_patterns) and len(s) < 40:
                continue
            lines.append(s)
        out.append((pno, ' '.join(lines)))
    return out

# ---------- sentence splitting ----------

def split_ko(text):
    # protect common abbreviations, then split on terminators
    text = re.sub(r'\s+', ' ', text)
    # Korean sentence enders: 다., 함., 됨., 임., 음., ?, !, 요., 습니다., 니다.
    parts = re.split(r'(?<=[다함됨임음니습갑니까하])\.(?=\s|[가-힣A-Z0-9“(\[]|$)|(?<=[?!.])\s+', text)
    out = []
    for p in parts:
        p = p.strip()
        p = re.sub(r'[^가-힣A-Za-z0-9 ?!.,()%·\-\u201c\u201d\u2018\u2019\'\"\[\]/:;·…$\u00b7\u2013\u2014&+~=×\uc790\uc2e4]+', ' ', p)
        p = re.sub(r'\s+', ' ', p).strip()
        if not p:
            continue
        # keep sentences with at least 8 hangul chars and a terminator or length>15
        if len(re.findall(r'[가-힣]', p)) >= 8:
            out.append(p)
    return out

def split_en(text):
    text = re.sub(r'\s+', ' ', text)
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z“(])', text)
    out = []
    for p in parts:
        p = p.strip()
        if len(p.split()) >= 6:
            out.append(p)
    return out

for name, path, kill, splitter in [
    ('ko', BASE + '\\ko_off_2022_main.txt', KILL_KO, split_ko),
    ('en', BASE + '\\en_off_2022_main.txt', KILL_EN, split_en),
]:
    pages = clean_pages(path, kill)
    sents = []
    for pno, body in pages:
        for s in splitter(body):
            sents.append({'page': pno, 'text': s})
    for i, s in enumerate(sents):
        s['idx'] = i
    with open(BASE + '\\%s_sentences.json' % name, 'w', encoding='utf-8') as f:
        json.dump(sents, f, ensure_ascii=False, indent=1)
    print(name, 'pages:', len(pages), 'sentences:', len(sents))
    print('sample:', sents[30]['text'][:120])
